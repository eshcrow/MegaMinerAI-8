#ifndef ANIMATIONENGINE_H
#define ANIMATIONENGINE_H

#include "animator.h"
#include "../../interfaces/ianimationengine.h"
#include "../common.h"

namespace visualizer
{
  // AnimationEngine will need to rely heavily on TimeManager
  // and trusting the renderer to give it the right frame.
  class _AnimationEngine: public Module, public IAnimationEngine
  {
    public:
      static void setup();
      static void destroy();
      SmartPointer<IAnimator> getAnimator();
    private:
     
  }; // _AnimationEngine

  extern _AnimationEngine *AnimationEngine;

} // visualizer


#endif
