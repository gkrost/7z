#!/usr/bin/env python3
import argparse
import json
import os
import random
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

OPT_FLAGS = ["-O2", "-O3", "-Ofast"]
MARCH_FLAGS = ["", "-march=native", "-march=core-avx2", "-march=x86-64-v3", "-march=x86-64-v4"]
MTUNE_FLAGS = ["", "-mtune=native", "-mtune=generic", "-mtune=core-avx2"]
LTO_FLAGS = ["", "-flto", "-flto=auto"]
OPTIONAL_FLAGS = [
    "-fno-plt",
    "-fomit-frame-pointer",
    "-funroll-loops",
    "-fno-tree-vectorize",
    "-fno-semantic-interposition",
    "-fipa-pta",
    "-maes",
    "-mpclmul",
    "-mavx2",
    "-mfma",
    "-mbmi",
    "-mbmi2",
    "-mavxvnni",
    "-mgfni",
    "-mvaes",
    "-mvpclmulqdq",
    "-mprefer-vector-width=256",
]

DICT_LINE_RE = re.compile(r"^\s*(\d+):\s+(\d+)\s+")


@dataclass(frozen=True)
class Candidate:
    opt: str
    march: str
    mtune: str
    lto: str
    toggles: tuple

    def flag_list(self, base_flags: str) -> list[str]:
        flags = [self.opt]
        if self.march:
            flags.append(self.march)
        if self.mtune:
            flags.append(self.mtune)
        flags.extend(self.toggles)
        if base_flags:
            flags.extend(base_flags.split())
        return flags

    def key(self) -> str:
        return "|".join([self.opt, self.march, self.mtune, self.lto, " ".join(self.toggles)])


def parse_speed(output: str, target: str, score_mode: str) -> float:
    compress_speeds = []
    decompress_speeds = []
    for raw_line in output.splitlines():
        if ":" not in raw_line:
            continue
        parts = raw_line.split("|")
        compress_part = parts[0] if parts else ""
        decompress_part = parts[1] if len(parts) > 1 else ""
        compress_match = DICT_LINE_RE.match(compress_part)
        if compress_match:
            compress_speeds.append(int(compress_match.group(2)))
        decompress_match = DICT_LINE_RE.match(decompress_part)
        if decompress_match:
            decompress_speeds.append(int(decompress_match.group(2)))

    if target == "compress":
        return score_values(compress_speeds, score_mode)
    if target == "decompress":
        return score_values(decompress_speeds, score_mode)
    compress_score = score_values(compress_speeds, score_mode)
    decompress_score = score_values(decompress_speeds, score_mode)
    return (compress_score + decompress_score) / 2.0


def score_values(values: list[int], score_mode: str) -> float:
    if not values:
        return 0.0
    if score_mode == "average":
        return sum(values) / len(values)
    return max(values)


def load_results(path: Path) -> dict[str, dict]:
    results = {}
    if not path.exists():
        return results
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            results[record["key"]] = record
    return results


def append_result(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def random_candidate(rng: random.Random) -> Candidate:
    toggles = tuple(flag for flag in OPTIONAL_FLAGS if rng.random() < 0.5)
    return Candidate(
        opt=rng.choice(OPT_FLAGS),
        march=rng.choice(MARCH_FLAGS),
        mtune=rng.choice(MTUNE_FLAGS),
        lto=rng.choice(LTO_FLAGS),
        toggles=toggles,
    )


def avoid_blacklist(candidate: Candidate, rng: random.Random, blacklist: set[str]) -> Candidate:
    attempts = 0
    current = candidate
    while current.key() in blacklist and attempts < 8:
        current = random_candidate(rng)
        attempts += 1
    return current


def mutate(candidate: Candidate, rng: random.Random, rate: float) -> Candidate:
    opt = candidate.opt
    march = candidate.march
    mtune = candidate.mtune
    lto = candidate.lto
    toggles = set(candidate.toggles)

    if rng.random() < rate:
        opt = rng.choice(OPT_FLAGS)
    if rng.random() < rate:
        march = rng.choice(MARCH_FLAGS)
    if rng.random() < rate:
        mtune = rng.choice(MTUNE_FLAGS)
    if rng.random() < rate:
        lto = rng.choice(LTO_FLAGS)
    for flag in OPTIONAL_FLAGS:
        if rng.random() < rate:
            if flag in toggles:
                toggles.remove(flag)
            else:
                toggles.add(flag)
    return Candidate(opt=opt, march=march, mtune=mtune, lto=lto, toggles=tuple(sorted(toggles)))


def crossover(a: Candidate, b: Candidate, rng: random.Random) -> Candidate:
    opt = rng.choice([a.opt, b.opt])
    march = rng.choice([a.march, b.march])
    mtune = rng.choice([a.mtune, b.mtune])
    lto = rng.choice([a.lto, b.lto])
    toggles = set(a.toggles)
    toggles ^= set(b.toggles)
    mixed = set(a.toggles)
    for flag in toggles:
        if rng.random() < 0.5:
            if flag in mixed:
                mixed.remove(flag)
            else:
                mixed.add(flag)
    return Candidate(opt=opt, march=march, mtune=mtune, lto=lto, toggles=tuple(sorted(mixed)))


def build_and_bench(candidate: Candidate, args: argparse.Namespace) -> tuple[float, str, str, str]:
    flags = " ".join(candidate.flag_list(args.base_flags))
    build_dir = Path(args.build_dir)
    bench_path = build_dir / args.program

    shutil.rmtree(build_dir, ignore_errors=True)

    make_cmd = [
        "make",
        "-f",
        args.makefile,
        f"O={build_dir}",
        f"CFLAGS_BASE2={flags}",
        f"CXXFLAGS_BASE2={flags}",
        f"FLAGS_FLTO={candidate.lto}",
        f"-j{args.jobs}",
        "-B",
    ]
    try:
        build_result = subprocess.run(
            make_cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=args.repo_root,
        )
    except subprocess.CalledProcessError as exc:
        return 0.0, "", exc.stderr or exc.stdout or str(exc), "build_failed"

    bench_cmd = [str(bench_path), "b"]
    try:
        result = subprocess.run(bench_cmd, check=True, capture_output=True, text=True, cwd=args.repo_root)
    except subprocess.CalledProcessError as exc:
        return 0.0, exc.stdout or "", exc.stderr or str(exc), "bench_failed"

    score = parse_speed(result.stdout, args.target, args.score_mode)
    return score, result.stdout, build_result.stderr, "ok"


def evolve(args: argparse.Namespace) -> None:
    rng = random.Random(args.seed)
    results_path = Path(args.results)
    cache = load_results(results_path) if args.resume else {}

    blacklist = set()
    if not args.blacklist_reset:
        blacklist = {key for key, record in cache.items() if record.get("status") not in (None, "ok")}

    population = [avoid_blacklist(random_candidate(rng), rng, blacklist) for _ in range(args.population)]
    population[0] = avoid_blacklist(
        Candidate(opt="-O2", march="", mtune="", lto="", toggles=tuple()),
        rng,
        blacklist,
    )

    best_record = None

    for generation in range(1, args.generations + 1):
        scores = []
        for candidate in population:
            key = candidate.key()
            if key in cache:
                record = cache[key]
                score = record["score"]
                if record.get("status") not in (None, "ok"):
                    blacklist.add(key)
                    score = 0.0
                scores.append((candidate, score))
                continue
            score, output, error, status = build_and_bench(candidate, args)
            if status != "ok":
                blacklist.add(key)
            record = {
                "key": key,
                "score": score,
                "flags": candidate.flag_list(args.base_flags),
                "lto": candidate.lto,
                "target": args.target,
                "score_mode": args.score_mode,
                "timestamp": time.time(),
                "generation": generation,
                "status": status,
                "error": error,
            }
            append_result(results_path, record)
            cache[key] = record
            if args.keep_logs:
                log_path = Path(args.keep_logs) / f"gen{generation}_{abs(hash(key))}.log"
                log_path.parent.mkdir(parents=True, exist_ok=True)
                log_path.write_text(output + ("\n" + error if error else ""), encoding="utf-8")
            scores.append((candidate, score))

        scores.sort(key=lambda item: item[1], reverse=True)
        top = scores[: args.elite]
        if top and (best_record is None or top[0][1] > best_record["score"]):
            best_record = {
                "score": top[0][1],
                "flags": top[0][0].flag_list(args.base_flags),
                "lto": top[0][0].lto,
            }

        next_population = [candidate for candidate, _ in top]
        while len(next_population) < args.population:
            parent_a = rng.choice(top)[0]
            parent_b = rng.choice(top)[0]
            child = mutate(crossover(parent_a, parent_b, rng), rng, args.mutation)
            next_population.append(avoid_blacklist(child, rng, blacklist))
        population = next_population

        if args.verbose:
            top_scores = scores[: max(args.top, 1)]
            summary = ", ".join(
                f"{candidate.key()}={score:.2f}" for candidate, score in top_scores
            )
            print(f"Generation {generation}: best score {scores[0][1]:.2f}")
            print(f"Top {len(top_scores)}: {summary}")

    if best_record:
        print("Best result")
        print(json.dumps(best_record, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evolve GCC flags for 7zz benchmark")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--makefile", default="makefile.gcc")
    parser.add_argument("--program", default="7zz")
    parser.add_argument("--build-dir", default="b/ga")
    parser.add_argument("--results", default="scripts/bench/results/evo_results.jsonl")
    parser.add_argument("--keep-logs", default="scripts/bench/results/logs")
    parser.add_argument("--target", choices=["compress", "decompress", "balanced"], default="compress")
    parser.add_argument("--score-mode", choices=["best", "average"], default="best")
    parser.add_argument("--generations", type=int, default=6)
    parser.add_argument("--population", type=int, default=6)
    parser.add_argument("--elite", type=int, default=2)
    parser.add_argument("--mutation", type=float, default=0.25)
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--base-flags", default="")
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", action="store_false", dest="resume")
    parser.add_argument("--blacklist-reset", action="store_true")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    evolve(args)


if __name__ == "__main__":
    main()
