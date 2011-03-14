#include "centralwidget.h"
#include "gui.h"
#include <QLabel>

CentralWidget::CentralWidget( QWidget *parent )
{
  m_renderWidget = new RenderWidget( this );
  m_widgetLayout = new QVBoxLayout( this );
  m_controlBarWidget = 
    (GOC_ControlBar*)GUI::getGUIObject( "ControlBar" );

  m_widgetLayout->addWidget( m_renderWidget );
  if( m_controlBarWidget )
  {
    if( 
        optionsMan::isInit() && 
        optionsMan::exists("maxControlHeight") 
      )
    {
      m_controlBarWidget->setMaximumHeight( 
          optionsMan::getInt( "maxControlHeight" )
          );
    }
    m_widgetLayout->addWidget( m_controlBarWidget );
  }
  
  setLayout( m_widgetLayout );

}