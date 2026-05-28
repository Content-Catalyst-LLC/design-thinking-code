program prototype_value_model
  implicit none

  integer, parameter :: n = 8
  character(len=96) :: names(n)
  real(8) :: learning_gain(n), feasibility_signal(n), user_response(n), equity_value(n), implementation_relevance(n)
  real(8) :: ethical_risk(n), operational_risk(n), technical_risk(n), scaling_risk(n)
  real(8) :: composite_risk(n), values(n)
  integer :: i

  names = [ character(len=96) :: &
    "Paper Service Blueprint", &
    "Clickable Interface Mockup", &
    "Role-Played Intake Scenario", &
    "Limited Workflow Pilot", &
    "Wizard-of-Oz Status Assistant", &
    "Exception-Case Service Simulation", &
    "Plain-Language Policy Mockup", &
    "Operational Tabletop Exercise" ]

  learning_gain = [8.6d0, 7.9d0, 8.2d0, 8.0d0, 8.4d0, 8.7d0, 8.1d0, 8.3d0]
  feasibility_signal = [7.1d0, 8.0d0, 7.4d0, 8.4d0, 7.2d0, 7.6d0, 8.2d0, 7.9d0]
  user_response = [8.0d0, 8.3d0, 8.5d0, 7.8d0, 8.2d0, 8.4d0, 8.0d0, 7.4d0]
  equity_value = [7.8d0, 7.0d0, 8.3d0, 7.7d0, 7.5d0, 8.6d0, 8.4d0, 7.8d0]
  implementation_relevance = [7.4d0, 7.8d0, 7.6d0, 8.7d0, 7.9d0, 8.3d0, 7.9d0, 8.6d0]

  ethical_risk = [3.8d0, 3.6d0, 4.2d0, 4.4d0, 5.1d0, 4.3d0, 3.2d0, 4.0d0]
  operational_risk = [4.2d0, 4.0d0, 4.5d0, 3.8d0, 4.8d0, 4.9d0, 3.6d0, 5.2d0]
  technical_risk = [2.8d0, 4.1d0, 3.0d0, 4.6d0, 5.4d0, 3.5d0, 2.6d0, 3.2d0]
  scaling_risk = [3.6d0, 4.0d0, 4.4d0, 4.8d0, 5.2d0, 5.0d0, 3.8d0, 5.5d0]

  do i = 1, n
    composite_risk(i) = 0.30d0 * ethical_risk(i) + &
                        0.30d0 * operational_risk(i) + &
                        0.20d0 * technical_risk(i) + &
                        0.20d0 * scaling_risk(i)

    values(i) = 0.25d0 * learning_gain(i) + &
                0.18d0 * feasibility_signal(i) + &
                0.20d0 * user_response(i) + &
                0.15d0 * equity_value(i) + &
                0.12d0 * implementation_relevance(i) - &
                0.10d0 * composite_risk(i)
  end do

  call sort_desc(names, values, composite_risk, n)

  print '(a)', 'rank,prototype,prototype_value,composite_risk'
  do i = 1, n
    print '(i0,a,a,a,f8.4,a,f8.4)', i, ',', trim(names(i)), ',', values(i), ',', composite_risk(i)
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

end program prototype_value_model
