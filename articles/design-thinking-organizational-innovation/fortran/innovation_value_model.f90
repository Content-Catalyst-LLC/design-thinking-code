program innovation_value_model
  implicit none

  integer, parameter :: n = 10
  character(len=128) :: names(n)
  real(8) :: desirability(n), feasibility(n), viability(n), equity(n)
  real(8) :: learning_value(n), implementation_readiness(n), risk(n), values(n)
  integer :: i

  names = [ character(len=128) :: &
    "Service Workflow Redesign", &
    "Self-Service Support Portal", &
    "AI Triage Assistant", &
    "Onboarding Simplification", &
    "Cross-Functional Escalation Model", &
    "Employee Knowledge Base Redesign", &
    "Customer Recovery Playbook", &
    "Manager Decision-Support Dashboard", &
    "Accessibility-First Service Redesign", &
    "Innovation Governance Cadence" ]

  desirability = [8.6d0, 7.9d0, 6.8d0, 9.0d0, 8.2d0, 8.4d0, 8.7d0, 7.4d0, 8.8d0, 7.8d0]
  feasibility = [7.3d0, 8.5d0, 5.9d0, 8.2d0, 6.8d0, 7.8d0, 7.6d0, 6.9d0, 7.0d0, 7.4d0]
  viability = [7.7d0, 8.2d0, 7.5d0, 8.1d0, 7.4d0, 7.9d0, 8.0d0, 7.8d0, 7.6d0, 8.0d0]
  equity = [8.1d0, 7.1d0, 5.8d0, 8.5d0, 7.8d0, 8.2d0, 8.0d0, 6.8d0, 9.2d0, 7.9d0]
  learning_value = [8.4d0, 7.2d0, 8.8d0, 7.6d0, 8.6d0, 7.5d0, 7.8d0, 8.2d0, 8.1d0, 8.7d0]
  implementation_readiness = [7.2d0, 8.0d0, 5.6d0, 8.1d0, 6.5d0, 7.4d0, 7.1d0, 6.3d0, 6.8d0, 7.0d0]
  risk = [3.6d0, 4.1d0, 6.8d0, 3.4d0, 5.1d0, 4.0d0, 3.8d0, 5.7d0, 4.3d0, 4.5d0]

  do i = 1, n
    values(i) = 0.22d0 * desirability(i) + &
                0.16d0 * feasibility(i) + &
                0.16d0 * viability(i) + &
                0.18d0 * equity(i) + &
                0.12d0 * learning_value(i) + &
                0.10d0 * implementation_readiness(i) - &
                0.06d0 * risk(i)
  end do

  call sort_desc(names, values, risk, n)

  print '(a)', 'rank,concept,design_value,risk'
  do i = 1, n
    print '(i0,a,a,a,f8.4,a,f8.4)', i, ',', trim(names(i)), ',', values(i), ',', risk(i)
  end do

contains

  subroutine sort_desc(names, values, risks, n)
    integer, intent(in) :: n
    character(len=128), intent(inout) :: names(n)
    real(8), intent(inout) :: values(n), risks(n)
    integer :: i, j
    real(8) :: temp_value, temp_risk
    character(len=128) :: temp_name

    do i = 1, n - 1
      do j = i + 1, n
        if (values(j) > values(i)) then
          temp_value = values(i)
          values(i) = values(j)
          values(j) = temp_value

          temp_risk = risks(i)
          risks(i) = risks(j)
          risks(j) = temp_risk

          temp_name = names(i)
          names(i) = names(j)
          names(j) = temp_name
        end if
      end do
    end do
  end subroutine sort_desc

end program innovation_value_model
