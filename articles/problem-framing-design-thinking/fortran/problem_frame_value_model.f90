program problem_frame_value_model
  implicit none

  integer, parameter :: n = 7
  character(len=64) :: names(n)
  real(8) :: explanatory_adequacy(n), stakeholder_coverage(n), opportunity_value(n), framing_risk(n)
  real(8) :: values(n)
  integer :: i

  names = [ character(len=64) :: &
    "Improve transit capacity", &
    "Improve transit reliability", &
    "Reduce commuter uncertainty", &
    "Redesign cross-network coordination", &
    "Reduce institutional travel burden", &
    "Rebuild trust in mobility services", &
    "Clarify service status and disruptions" ]

  explanatory_adequacy = [7.2d0, 8.3d0, 8.6d0, 8.0d0, 8.4d0, 8.1d0, 7.9d0]
  stakeholder_coverage = [6.8d0, 7.9d0, 7.5d0, 8.7d0, 8.2d0, 8.5d0, 7.6d0]
  opportunity_value    = [7.1d0, 8.2d0, 8.5d0, 8.4d0, 8.1d0, 8.3d0, 8.0d0]
  framing_risk         = [4.8d0, 3.9d0, 3.7d0, 4.2d0, 3.8d0, 4.1d0, 3.6d0]

  do i = 1, n
    values(i) = 0.30d0 * explanatory_adequacy(i) + &
                0.25d0 * stakeholder_coverage(i) + &
                0.30d0 * opportunity_value(i) - &
                0.15d0 * framing_risk(i)
  end do

  call sort_desc(names, values, n)

  print '(a)', 'rank,frame,frame_value'
  do i = 1, n
    print '(i0,a,a,a,f8.4)', i, ',', trim(names(i)), ',', values(i)
  end do

contains

  subroutine sort_desc(names, values, n)
    integer, intent(in) :: n
    character(len=64), intent(inout) :: names(n)
    real(8), intent(inout) :: values(n)
    integer :: i, j
    real(8) :: temp_value
    character(len=64) :: temp_name

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

end program problem_frame_value_model
