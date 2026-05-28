program insight_value_model
  implicit none

  integer, parameter :: n = 8
  character(len=96) :: names(n)
  real(8) :: pattern_support(n), explanatory_depth(n), opportunity_value(n), interpretive_risk(n)
  real(8) :: values(n)
  integer :: i

  names = [ character(len=96) :: &
    "Users want clarity more than feature variety", &
    "Waiting uncertainty produces more frustration than waiting time itself", &
    "Staff workarounds reveal hidden system failure points", &
    "Users interpret procedural silence as institutional indifference", &
    "People ask for more information when they actually need confidence", &
    "Drop-off points reveal institutional burden rather than low motivation", &
    "Repeated calls reveal missing ownership rather than user dependency", &
    "Avoidance behavior signals trust breakdown more than preference" ]

  pattern_support   = [8.3d0, 8.7d0, 8.1d0, 7.8d0, 8.0d0, 8.4d0, 7.9d0, 7.7d0]
  explanatory_depth = [7.9d0, 8.4d0, 8.6d0, 8.2d0, 8.3d0, 8.5d0, 8.1d0, 8.4d0]
  opportunity_value = [8.1d0, 8.5d0, 8.3d0, 7.9d0, 8.4d0, 8.6d0, 8.2d0, 8.0d0]
  interpretive_risk = [3.8d0, 3.6d0, 4.1d0, 4.3d0, 3.9d0, 4.2d0, 4.0d0, 4.5d0]

  do i = 1, n
    values(i) = 0.30d0 * pattern_support(i) + &
                0.30d0 * explanatory_depth(i) + &
                0.25d0 * opportunity_value(i) - &
                0.15d0 * interpretive_risk(i)
  end do

  call sort_desc(names, values, n)

  print '(a)', 'rank,insight,insight_value'
  do i = 1, n
    print '(i0,a,a,a,f8.4)', i, ',', trim(names(i)), ',', values(i)
  end do

contains

  subroutine sort_desc(names, values, n)
    integer, intent(in) :: n
    character(len=96), intent(inout) :: names(n)
    real(8), intent(inout) :: values(n)
    integer :: i, j
    real(8) :: temp_value
    character(len=96) :: temp_name

    do i = 1, n - 1
      do j = i + 1, n
        if (values(j) > values(i)) then
          temp_value = values(i)
          values(i) = values(j)
          values(j) = temp_value

          temp_name = names(i)
          names(i) = names(j)
          names(j) = temp_name
        end if
      end do
    end do
  end subroutine sort_desc

end program insight_value_model
