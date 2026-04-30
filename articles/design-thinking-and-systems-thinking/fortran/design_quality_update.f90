program design_quality_update
  implicit none

  integer :: t
  real :: quality
  real, parameter :: insight_gain = 0.70
  real, parameter :: usability = 0.65
  real, parameter :: friction = 0.25
  real, parameter :: rate = 0.07

  quality = 0.35

  print *, "Iteration", "Quality"

  do t = 1, 16
     quality = quality + rate * (insight_gain + usability - friction)
     if (quality > 1.0) quality = 1.0
     if (quality < 0.0) quality = 0.0
     print *, t, quality
  end do

end program design_quality_update
