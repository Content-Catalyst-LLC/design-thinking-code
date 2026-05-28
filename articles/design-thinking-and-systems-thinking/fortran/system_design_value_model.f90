program system_design_value_model
  implicit none

  integer, parameter :: n = 8
  character(len=96) :: names(n)
  real(8) :: human(n), leverage(n), feasibility(n), equity(n), durability(n), risk(n), values(n)
  integer :: i

  names = [ character(len=96) :: &
    "Service Navigation Redesign", &
    "Eligibility Rule Simplification", &
    "Information Flow Dashboard", &
    "Cross-Agency Referral Protocol", &
    "Participatory Governance Review", &
    "Community Support Infrastructure", &
    "Burden-Aware Intake Redesign", &
    "Institutional Learning Loop" ]

  human = [8.7d0, 8.1d0, 7.2d0, 7.8d0, 7.6d0, 8.4d0, 8.6d0, 7.7d0]
  leverage = [6.8d0, 8.6d0, 8.2d0, 8.4d0, 8.7d0, 8.0d0, 7.4d0, 8.8d0]
  feasibility = [8.1d0, 6.9d0, 7.8d0, 6.7d0, 6.3d0, 7.1d0, 7.7d0, 7.0d0]
  equity = [7.9d0, 8.2d0, 7.4d0, 7.8d0, 8.8d0, 8.6d0, 8.5d0, 8.0d0]
  durability = [7.5d0, 8.3d0, 7.6d0, 8.1d0, 8.5d0, 8.0d0, 7.6d0, 8.6d0]
  risk = [3.5d0, 4.7d0, 4.0d0, 5.1d0, 5.3d0, 4.6d0, 4.1d0, 4.8d0]

  do i = 1, n
    values(i) = 0.24d0 * human(i) + &
                0.26d0 * leverage(i) + &
                0.18d0 * feasibility(i) + &
                0.14d0 * equity(i) + &
                0.12d0 * durability(i) - &
                0.06d0 * risk(i)
  end do

  call sort_desc(names, values, risk, n)

  print '(a)', 'rank,intervention,system_design_value,risk'
  do i = 1, n
    print '(i0,a,a,a,f8.4,a,f8.4)', i, ',', trim(names(i)), ',', values(i), ',', risk(i)
  end do

contains

  subroutine sort_desc(names, values, risks, n)
    integer, intent(in) :: n
    character(len=96), intent(inout) :: names(n)
    real(8), intent(inout) :: values(n), risks(n)
    integer :: i, j
    real(8) :: temp_value, temp_risk
    character(len=96) :: temp_name

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

end program system_design_value_model
