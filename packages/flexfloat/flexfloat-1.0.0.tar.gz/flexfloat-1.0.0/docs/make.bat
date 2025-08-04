@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

if "%1" == "help" (
	:help
	%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
	goto end
)

if "%1" == "clean" (
	echo.Cleaning build directory...
	rmdir /s /q %BUILDDIR% >nul 2>&1
	echo.Build directory cleaned.
	goto end
)

if "%1" == "html" (
	echo.Building HTML documentation...
	%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%\html %SPHINXOPTS% %O%
	if errorlevel 1 exit /b 1
	echo.
	echo.Build finished. The HTML pages are in %BUILDDIR%\html.
	goto end
)

if "%1" == "livehtml" (
	echo.Starting live HTML build server...
	sphinx-autobuild %SOURCEDIR% %BUILDDIR%\html %SPHINXOPTS% %O%
	goto end
)

if "%1" == "linkcheck" (
	echo.Checking external links...
	%SPHINXBUILD% -b linkcheck %SOURCEDIR% %BUILDDIR%\linkcheck %SPHINXOPTS% %O%
	if errorlevel 1 exit /b 1
	echo.
	echo.Link check complete; look for any errors in the above output or in %BUILDDIR%\linkcheck\output.txt.
	goto end
)

if "%1" == "strict" (
	echo.Building HTML documentation with warnings as errors...
	%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%\html -W %SPHINXOPTS% %O%
	if errorlevel 1 exit /b 1
	echo.
	echo.Build finished successfully with no warnings.
	goto end
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:end
popd
