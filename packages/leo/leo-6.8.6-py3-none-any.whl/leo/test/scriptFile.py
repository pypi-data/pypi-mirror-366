#@+leo-ver=5-thin
#@+node:ekr.20170911061827.1: * @button check .leo files
'''Make sure no distributed .leo file contains xml-stylesheet elements.'''
# g.cls()
#@+<< define files >>
#@+node:ekr.20170911062209.1: ** << define files >>
files = (
    'config/exampleSettings.leo',
    'config/leoSettings.leo',
    'core/leoPyRef.leo',
    'dist/leoDist.leo',
    'doc/LeoReleaseNotes.leo',
    'doc/cheatSheet.leo',
    'doc/default_workbook.leo',
    'doc/leoDocs.leo',
    'doc/leoSlideShows.leo',
    'doc/quickstart.leo',
    'external/leo2html.leo',
    'plugins/leoGuiPluginsRef.leo',
    'scripts/scripts.leo',
    'test/test.leo',
)
#@-<< define files >>
for fn in files:
    path = g.os_path_finalize_join(g.app.loadDir, '..', fn)
    if g.os_path_exists(path):
        with open(path, 'rb') as f:
            s = f.read()
        s = g.toUnicode(s)
        if s.find('<xml-stylesheet') > -1:
            g.es_print('contains xml-stylesheet element: %s' % (path))
    else:
        g.es_print('does not exist: %s' % path)
g.es_print('done')
#@-leo

