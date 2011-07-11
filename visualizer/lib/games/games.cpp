#include "games.h"

_Games *Games = 0;

void _Games::setup()
{
  if( !Games )
  {
    Games = new _Games;
  }
  else
  {
    THROW( Exception, "Games Loader is already initialized." );
  }

  Games->_setup();
}

#include <iostream>
using namespace std;

void _Games::_setup()
{
  IGame *game = 0;
  bool pluginFound;
  QDir pluginsDir( qApp->applicationDirPath() );
  pluginsDir.cd( "plugins" );
  foreach( QString fileName, pluginsDir.entryList( QDir::Files ) )
  {
#if __DEBUG__
    cerr << "Loading Plugin: " << qPrintable( pluginsDir.absoluteFilePath( fileName ) ) << endl;
#endif
    QPluginLoader pluginLoader( pluginsDir.absoluteFilePath( fileName ) );
    QObject *plugin = pluginLoader.instance();
    pluginFound = false;
    if( plugin )
    {
      game = qobject_cast<IGame *>( plugin );
      if( game )
      {
        pluginFound = true;
        m_gameList.push_back( game );
      }
    }

    if( !pluginFound )
    {
      THROW( Exception, "The Above Plugin Did Not Load Correctly" );
    }
  }
}

std::vector< IGame* > _Games::gameList()
{
  return m_gameList;
}

void _Games::destroy()
{
  delete Games;
  Games = 0;

}
