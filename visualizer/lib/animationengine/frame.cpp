#include "frame.h"

namespace visualizer
{
  void Frame::addAnimatable( const SmartPointer<Animatable>& animatable )
  {
    m_frame.push_back( animatable );
  }

  std::list<SmartPointer<Animatable> >& Frame::getFrame()
  {
    return m_frame;
  }

  const size_t Frame::size() const
  {
    return m_frame.size();
  }

} // visualizer
