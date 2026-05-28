program design_value_model
  implicit none

  integer, parameter :: n = 5
  character(len=64) :: names(n)
  real(8) :: human_relevance(n), feasibility(n), learning_value(n), residual_risk(n)
  real(8) :: values(n)
  integer :: i

  names = [ character(len=64) :: &
    "Service Redesign Pathway", &
    "Digital Platform Pathway", &
    "Workflow Coordination Pathway", &
    "Community Partnership Pathway", &
    "Participatory Governance Pathway" ]

  human_relevance = [8.8d0, 7.9d0, 8.2d0, 8.6d0, 8.9d0]
  feasibility     = [7.4d0, 8.3d0, 7.8d0, 7.1d0, 6.8d0]
  learning_value  = [8.1d0, 7.7d0, 8.4d0, 8.5d0, 8.9d0]
  residual_risk   = [4.0d0, 4.3d0, 3.8d0, 4.2d0, 4.8d0]

  do i = 1, n
    values(i) = 0.35d0 * human_relevance(i) + &
                0.25d0 * feasibility(i) + &
                0.25d0 * learning_value(i) - &
                0.15d0 * residual_risk(i)
  end do

  call sort_desc(names, values, n)

  print '(a)', 'rank,pathway,design_value'
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

end program design_value_model
