#ifndef IOPTIONSMAN_H
#define IOPTIONSMAN_H

#include "../lib/optionsmanager/option.h"
#include <string>
#include <QtPlugin>

namespace visualizer
{

typedef std::string OptID_t;

class IOptionsMan
{
  public:
    virtual bool loadOptionFile( const std::string& filename ) = 0;
    virtual bool saveOptionFile( const std::string& filename ) = 0;
    virtual OptionBase* operator() ( const OptID_t& oName ) = 0;

    virtual bool exists( const OptID_t& oName ) = 0;
    virtual OptionType optionType( const OptID_t& oName ) = 0;

    virtual bool addString( const OptID_t& oName, const std::string& val ) = 0;
    virtual bool addInt( const OptID_t& oName, const int& val ) = 0;
    virtual bool addFloat( const OptID_t& oName, const float& val ) = 0;
    virtual bool addBool( const OptID_t& oName, const bool& val ) = 0;

};

Q_DECLARE_INTERFACE( IOptionsMan, "siggame.vis2.optionsman/0.1" );

} // visualizer

#endif
