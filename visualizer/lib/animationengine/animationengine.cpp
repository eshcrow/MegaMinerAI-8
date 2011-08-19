#include "animationengine.h"

namespace visualizer
{
  _AnimationEngine *AnimationEngine = 0;

  _AnimationEngine::_AnimationEngine()
  {
    m_frameList = 0;

  } // _AnimationEngine::_AnimationEngine()

  void _AnimationEngine::setup()
  {
    if( !AnimationEngine )
    {
      AnimationEngine = new _AnimationEngine;
    }
    else
    {
      THROW( Exception, "Animation Engine already initialized." );
    }

  } // _AnimationEngine::setup()

  void _AnimationEngine::destroy()
  {
    delete AnimationEngine;
    AnimationEngine = 0;

  } // _AnimationEngine::destroy()

  void _AnimationEngine::buildAnimations( Frame& frame )
  {
    // @NOTE Can we simplify this looping any?  Not a huge issue since it's internal
    // if this were on the piracy side, I'd be a little more worried
    for
      ( 
      std::list<SmartPointer<Animatable> >::iterator i = frame.getAnimations().begin();
      i != frame.getAnimations().end();
      i++ 
      )
    {
      float totalDuration = 0;
      float extraTime = 0;
      float exT;
      for
        (
        std::list<SmartPointer<Anim> >::iterator j = (*i)->getFrames().begin();
        j != (*i)->getFrames().end();
        j++
        )
      {
        totalDuration += (*j)->controlDuration();
        exT = (*j)->totalDuration() - (*j)->controlDuration();
        extraTime = extraTime > exT ? extraTime : exT;

      }

      float fullTime = totalDuration + extraTime;
      float start = 0;
      for
        (
        std::list<SmartPointer<Anim> >::iterator j = (*i)->getFrames().begin();
        j != (*i)->getFrames().end();
        j++
        )
      {
        (*j)->startTime = start;
        start = (*j)->endTime = (*j)->startTime + ((*j)->controlDuration()/fullTime);
      }

    }

  } // _AnimationEngine::buildAnimations()

  void _AnimationEngine::draw()
  {
    if( m_frameList )
    {
#if 1
      //cout << "Turn: " << TimeManager->getTurn() << endl;
      Frame& frame = (*m_frameList)[ TimeManager->getTurn() ];

      //cout << "Frame size: " << frame.size() << endl;
      //cout << "Anims: " << frame.getAnimations().size() << endl;

      for
        (
        std::list<SmartPointer<Animatable> >::iterator i = frame.getAnimations().begin();
        i != frame.getAnimations().end();
        i++
        )
      {
        cout << "Draw: " << (*i)->numKeyFrames() << endl;
        drawAnim( *(*i) );
      }
#endif
    }

  } // _AnimationEngine::draw()

  void _AnimationEngine::drawAnim( const Animatable& animator )
  {
    int c = 0;
    for
      (
      std::list<SmartPointer<Anim> >::const_iterator i = animator.getFrames().begin();
      i != animator.getFrames().end();
      i++
      )
    {
      cout << "C: " << c++ << endl;
    }

  } // _AnimationEngine::drawAnim()

  void _AnimationEngine::registerFrameContainer( AnimSequence* frameList )
  {
    cout << "REGISTERED" << endl;
    m_frameList = frameList;
    cout << "mSize: " << m_frameList->size() << endl;
  } // _AnimationEngine::registerFrameContainer()

} // visualizer


