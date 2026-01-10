## Replace unsafe C string functions with safe alternatives

**Priority**: High (Security)  
**Category**: Security Vulnerability  
**Affected Files**: Multiple C/C++ files

### Description

The codebase contains multiple uses of unsafe C string functions that are prone to buffer overflows and security vulnerabilities. These functions should be replaced with their safe counterparts.

### Findings

#### sprintf usage (should use snprintf) - 11 instances:
- `C/Util/7z/7zMain.c:501` - commented out sprintf
- `CPP/7zip/Archive/FlvHandler.cpp:225` - `sprintf(temp, " = %.3f", d);`
- `CPP/7zip/UI/Common/OpenArchive.cpp:1324` - `sprintf(temp, "%s %d", s, n);`
- `CPP/7zip/UI/FileManager/Panel.cpp:678` - sprintf usage
- `CPP/7zip/UI/FileManager/Panel.cpp:886` - sprintf usage
- `CPP/7zip/UI/FileManager/PanelItems.cpp:916` - sprintf usage
- `CPP/7zip/UI/FileManager/PanelItems.cpp:927` - sprintf usage
- `CPP/7zip/UI/FileManager/SysIconUtils.cpp:234` - sprintf usage
- `CPP/7zip/UI/FileManager/SysIconUtils.cpp:266` - sprintf usage
- `CPP/7zip/UI/FileManager/PanelListNotify.cpp:236` - sprintf usage
- `CPP/7zip/UI/FileManager/PanelListNotify.cpp:246` - sprintf usage

#### Redefinition of unsafe functions:
- `C/Util/7zipInstall/7zipInstall.c:49-51` - defines wcscat/wcscpy as lstrcatW/lstrcpyW
- `C/Util/7zipUninstall/7zipUninstall.c:41-43` - defines wcscat/wcscpy
- `C/Util/SfxSetup/SfxSetup.c:30-32` - defines wcscat/wcscpy

#### Commented-out unsafe calls:
- `C/DllSecur.c:92` - `// lstrcatW(buf, L".dll");`
- `CPP/7zip/Archive/MbrHandler.cpp:608-609` - commented strcat/strcpy

#### Undefining sprintf:
- `CPP/7zip/UI/Common/ArchiveCommandLine.cpp:5` - `#undef sprintf`
- `CPP/7zip/UI/Common/ArchiveExtractCallback.cpp:5` - `#undef sprintf`

### Security Impact

Buffer overflow vulnerabilities can lead to:
- Remote code execution
- Denial of service
- Data corruption
- Information disclosure

### Recommended Actions

1. **Replace sprintf with snprintf**: 
   ```c
   // Before
   sprintf(temp, " = %.3f", d);
   
   // After
   snprintf(temp, sizeof(temp), " = %.3f", d);
   ```

2. **Replace strcpy/strcat with safer and more portable alternatives**:
   ```c
   // Prefer bounded functions like strncpy and strncat, ensuring explicit null-termination.
   // Where available, use strlcpy and strlcat instead of strncpy/strncat for better semantics.
   // On Windows/MSVC specifically, you may use strcpy_s, strcat_s, wcsncpy_s, and wcsncat_s.
   ```

3. **Conduct security audit** of all string manipulation code

4. **Add static analysis** to detect unsafe function usage in CI/CD pipeline

5. **Consider using safer C++ string classes** where appropriate

### References

- CWE-120: Buffer Copy without Checking Size of Input
- CWE-134: Use of Externally-Controlled Format String
- CERT C Coding Standard: STR07-C
