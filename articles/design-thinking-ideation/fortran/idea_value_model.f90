program idea_value_model
  implicit none

  integer, parameter :: n = 8
  character(len=96) :: names(n)
  real(8) :: desirability(n), feasibility(n), novelty(n), equity_value(n), learning_value(n), residual_risk(n)
  real(8) :: values(n)
  integer :: i

  names = [ character(len=96) :: &
    "Peer Support Navigation Model", &
    "Self-Service Digital Triage", &
    "Mobile Outreach Partnership", &
    "AI-Assisted Intake Guidance", &
    "Status Visibility and Ownership Dashboard", &
    "Community-Based Service Liaison Model", &
    "Plain-Language Decision Guide", &
    "Exception Handling Workflow Redesign" ]

  desirability  = [8.4d0, 7.8d0, 8.6d0, 7.4d0, 8.2d0, 8.7d0, 8.1d0, 8.0d0]
  feasibility   = [7.3d0, 8.2d0, 7.0d0, 6.8d0, 7.6d0, 6.9d0, 8.4d0, 7.1d0]
  novelty       = [7.6d0, 7.2d0, 8.1d0, 8.5d0, 7.8d0, 8.0d0, 6.9d0, 7.7d0]
  equity_value  = [8.1d0, 6.8d0, 8.7d0, 6.9d0, 7.9d0, 8.8d0, 8.2d0, 8.0d0]
  learning_value= [8.0d0, 7.6d0, 8.2d0, 8.4d0, 8.1d0, 8.5d0, 7.8d0, 8.3d0]
  residual_risk = [4.0d0, 3.8d0, 4.5d0, 5.2d0, 4.2d0, 4.7d0, 3.4d0, 4.6d0]

  do i = 1, n
    values(i) = 0.24d0 * desirability(i) + &
                0.18d0 * feasibility(i) + &
                0.18d0 * novelty(i) + &
                0.18d0 * equity_value(i) + &
                0.12d0 * learning_value(i) - &
                0.10d0 * residual_risk(i)
  end do

  call sort_desc(names, values, n)

  print '(a)', 'rank,idea,idea_value'
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

end program idea_value_model
