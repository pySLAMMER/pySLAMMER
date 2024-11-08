@ECHO OFF

REM Minimal make.bat for Sphinx documentation

if "%SPHINXBUILD%" == "" (
    set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build

%SPHINXBUILD% -M html %SOURCEDIR% %BUILDDIR%
