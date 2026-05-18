@ECHO OFF
REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set BUILDDIR=_build
set ALLSPHINXOPTS=-d %BUILDDIR%\doctrees %SPHINXOPTS%
set SPHINXOPTS=

if NOT "%PAPER%" == "" (
	set ALLSPHINXOPTS=-D latex_paper_size=%PAPER% %ALLSPHINXOPTS%
)

:commands
if "%1" == "" goto help

%SPHINXBUILD% -M %1 %BUILDDIR% %ALLSPHINXOPTS% %SPHINXBUILD_OPTS%
goto end

:help
%SPHINXBUILD% -M help %BUILDDIR% %ALLSPHINXOPTS% %SPHINXBUILD_OPTS%

:end
popd