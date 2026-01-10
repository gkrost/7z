## Update deprecated Windows API usage (GetVersion)

**Priority**: Medium (Future Compatibility)  
**Category**: Deprecated API  
**Affected Files**: `C/DllSecur.c`

### Description

The code uses the deprecated `GetVersion()` Windows API function, which has been marked as deprecated since Windows 8.1. This API can return incorrect version information on Windows 10+ and should be replaced with version helper functions.

### Location

`C/DllSecur.c:44-54`

### Current Code

```c
#ifdef __clang__
  #pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#endif
#if defined (_MSC_VER) && _MSC_VER >= 1900
// sysinfoapi.h: kit10: GetVersion was declared deprecated
#pragma warning(disable : 4996)
#endif

#define IF_NON_VISTA_SET_DLL_DIRS_AND_RETURN \
    if ((UInt16)GetVersion() != 6) { \  // ⚠️ Deprecated API
      const \
       Func_SetDefaultDllDirectories setDllDirs = \
      (Func_SetDefaultDllDirectories) Z7_CAST_FUNC_C GetProcAddress(GetModuleHandle(TEXT("kernel32.dll")), \
           "SetDefaultDllDirectories"); \
      if (setDllDirs) if (setDllDirs(MY_LOAD_LIBRARY_SEARCH_SYSTEM32 | MY_LOAD_LIBRARY_SEARCH_USER_DIRS)) return; }
```

Usage:
- Line 59: `My_SetDefaultDllDirectories()`
- Line 68: `LoadSecurityDlls()`

### Issues

1. **Deprecated API**: `GetVersion()` is officially deprecated since Windows 8.1
2. **Incorrect Results**: On Windows 10+, `GetVersion()` may return Windows 8 version due to compatibility shims unless the application has a manifest
3. **Disabled Warnings**: Code uses `#pragma` to suppress deprecation warnings instead of fixing the issue
4. **Fragile Version Check**: Checking for Vista (version 6) using major version only is fragile

### Impact

- May not work correctly on future Windows versions
- Microsoft may remove this API entirely in future updates
- Application behavior may be inconsistent depending on manifest settings

### Recommended Solution

Replace `GetVersion()` with Windows Version Helper APIs:

```c
#include <VersionHelpers.h>

// Instead of checking for non-Vista using the deprecated GetVersion():
// if ((UInt16)GetVersion() != 6)
//
// Use Version Helper APIs to skip only Vista and Windows 7 (both 6.x):
if (!IsWindowsVistaOrGreater() || IsWindows8OrGreater())
```

Note: The original code checks `(UInt16)GetVersion() != 6`, which matches any OS where the major version is NOT 6 (i.e., XP/Server 2003 with version 5.x, or Windows 10+ with version 10.x). To replicate this behavior, we check if the OS is either below Vista OR Windows 8 or greater.

Or for more precise control, define a helper:

```c
#include <VersionHelpers.h>

// Returns TRUE if NOT in the Vista/7/8 family (version 6.x)
BOOL IsNonVista6Family() 
{
    return !IsWindowsVistaOrGreater() || IsWindows8Point1OrGreater();
}

#define IF_NON_VISTA_SET_DLL_DIRS_AND_RETURN \
    if (IsNonVista6Family()) { \
      // ... rest of macro
```

### Alternative Approaches

If Version Helpers are not available (very old SDK):

1. **Use VerifyVersionInfo**:
   ```c
   BOOL IsWindowsVersionOrGreater(WORD major, WORD minor, WORD servpack)
   {
       OSVERSIONINFOEXW osvi = { sizeof(osvi), 0, 0, 0, 0, {0}, 0, 0 };
       DWORDLONG        const dwlConditionMask = 
           VerSetConditionMask(
           VerSetConditionMask(
           VerSetConditionMask(
               0, VER_MAJORVERSION, VER_GREATER_EQUAL),
                  VER_MINORVERSION, VER_GREATER_EQUAL),
                  VER_SERVICEPACKMAJOR, VER_GREATER_EQUAL);

       osvi.dwMajorVersion = major;
       osvi.dwMinorVersion = minor;
       osvi.wServicePackMajor = servpack;

       return VerifyVersionInfoW(&osvi, 
           VER_MAJORVERSION | VER_MINORVERSION | VER_SERVICEPACKMAJOR,
           dwlConditionMask) != FALSE;
   }
   ```

2. **Use RtlGetVersion** (requires DDK/WDK):
   ```c
   typedef LONG (WINAPI *RtlGetVersionPtr)(PRTL_OSVERSIONINFOW);
   
   BOOL GetTrueWindowsVersion(DWORD *major, DWORD *minor)
   {
       HMODULE hMod = GetModuleHandleW(L"ntdll.dll");
       if (hMod) {
           RtlGetVersionPtr RtlGetVersion = 
               (RtlGetVersionPtr)GetProcAddress(hMod, "RtlGetVersion");
           if (RtlGetVersion) {
               RTL_OSVERSIONINFOW osvi = { 0 };
               osvi.dwOSVersionInfoSize = sizeof(osvi);
               if (RtlGetVersion(&osvi) == 0) {
                   *major = osvi.dwMajorVersion;
                   *minor = osvi.dwMinorVersion;
                   return TRUE;
               }
           }
       }
       return FALSE;
   }
   ```

### Testing

Test on:
- Windows Vista (6.0)
- Windows 7 (6.1)
- Windows 8 (6.2)
- Windows 8.1 (6.3)
- Windows 10 (10.0)
- Windows 11 (10.0 with higher build number)

### References

- [GetVersion function (sysinfoapi.h) - Microsoft Docs](https://docs.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-getversion)
- [Version Helper functions - Microsoft Docs](https://docs.microsoft.com/en-us/windows/win32/sysinfo/version-helper-apis)
- [Operating System Version - Microsoft Docs](https://docs.microsoft.com/en-us/windows/win32/sysinfo/operating-system-version)
