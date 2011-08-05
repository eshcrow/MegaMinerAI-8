#ifndef IANIMATIONENGINE_H
#define IANIMATIONENGINE_H

#include <QtPlugin>
#include <list>
#include <vector>
#include "common.h"

namespace visualizer
{
  struct Anim
  {
    virtual float controlDuration() const = 0;
    virtual float totalDuration() const = 0;
    float startTime; 
    float endTime;
  }; // Anim

  struct AnimData
  {
  }; // AnimData

  struct IAnimator
  {
    virtual void addKeyFrame( const SmartPointer<Anim>& a ) = 0;
    virtual void addSubFrame( const size_t& keyFrame, const SmartPointer<Anim>& a ) = 0;

    virtual const size_t& numKeyFrames() = 0;

  }; // IAnimator
  
  class IAnimationEngine
  {
    public:
      virtual SmartPointer<IAnimator> getAnimator() = 0;
  }; // IAnimationEngine

  class IFrame
  {
    public:
  }; // IFrame

  class IFrameContainer
  {
    public:
      
  }; // IFrameContainer

/////////////////////////////////////////////////
/// @class Animatable 
/// @brief Base Class for any object you want to associate animations with.
/////////////////////////////////////////////////

/////////////////////////////////////////////////
/// @fn Animatable::getAnimationSequence( IAnimationEngine* animEngine )
/// @brief Gets the IAnimator defined by the core engine and saves it.
/// @param animEngine The interface to the core engine passed through on 
///  initialization.
/////////////////////////////////////////////////

/////////////////////////////////////////////////
/// @fn Animatable::getData()
/// @brief Virtual function which gets the 
/// animation specific storage structure the 
/// animator uses. 
////////////////////////////////////////////////

  class Animatable
  {
    public:
      IAnimator& getAnimationSequence( IAnimationEngine* animEngine )
      {
        if( !m_animationSequence )
        {
          m_animationSequence = animEngine->getAnimator();
        }
        return *m_animationSequence;
      }

      virtual AnimData* getData() = 0; 

    private:
      SmartPointer<IAnimator> m_animationSequence;

  }; // Animatable

  class AnimSequence
  {
    public:
    //TODO: Update to Frame
      void addFrame( const Frame& frame )
      {
        m_frames.push_back( frame );
      }

      const size_t size() const
      {
        return m_frames.size();
      }

     private:
      std::list<Frame> m_frames;
  };

} // visualizer

Q_DECLARE_INTERFACE( visualizer::IAnimationEngine, "siggame.vis2.animationengine/0.1" );
Q_DECLARE_INTERFACE( visualizer::IAnimator, "siggame.vis2.animator/0.1" );

#endif
