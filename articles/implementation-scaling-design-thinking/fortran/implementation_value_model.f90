program implementation_value_model
  implicit none

  integer, parameter :: n = 8
  character(len=96) :: names(n)
  real(8) :: adoption(n), operations(n), durability(n), governance(n), equity(n), finance(n)
  real(8) :: operational_risk(n), governance_risk(n), technical_risk(n), equity_risk(n), financial_risk(n)
  real(8) :: composite_risk(n), values(n)
  integer :: i

  names = [ character(len=96) :: &
    "Digital Intake Workflow", &
    "Frontline Service Playbook", &
    "Cross-Team Escalation Protocol", &
    "Community Outreach Scheduling Tool", &
    "Status Visibility Service", &
    "Implementation Learning Dashboard", &
    "Training and Support System", &
    "Equity Monitoring Protocol" ]

  adoption = [8.3d0, 7.8d0, 7.1d0, 8.0d0, 8.2d0, 7.7d0, 7.9d0, 7.3d0]
  operations = [7.9d0, 8.4d0, 7.6d0, 7.2d0, 7.8d0, 8.1d0, 8.2d0, 7.4d0]
  durability = [7.5d0, 8.1d0, 7.8d0, 7.0d0, 7.7d0, 8.2d0, 8.0d0, 8.3d0]
  governance = [7.2d0, 7.6d0, 8.3d0, 7.1d0, 7.4d0, 8.4d0, 7.8d0, 8.5d0]
  equity = [7.3d0, 7.9d0, 7.5d0, 8.5d0, 7.8d0, 7.6d0, 8.1d0, 8.7d0]
  finance = [7.4d0, 8.0d0, 7.6d0, 7.2d0, 7.3d0, 7.7d0, 7.6d0, 7.4d0]

  operational_risk = [4.1d0, 3.8d0, 4.6d0, 4.3d0, 4.0d0, 3.9d0, 3.7d0, 4.2d0]
  governance_risk = [4.5d0, 3.9d0, 3.7d0, 4.4d0, 4.2d0, 3.6d0, 3.8d0, 3.5d0]
  technical_risk = [4.7d0, 2.8d0, 3.1d0, 4.2d0, 4.8d0, 4.4d0, 3.2d0, 3.4d0]
  equity_risk = [4.2d0, 3.7d0, 4.0d0, 3.5d0, 4.1d0, 3.9d0, 3.6d0, 3.2d0]
  financial_risk = [4.4d0, 3.5d0, 3.8d0, 4.6d0, 4.7d0, 3.8d0, 3.9d0, 4.1d0]

  do i = 1, n
    composite_risk(i) = 0.25d0 * operational_risk(i) + &
                        0.22d0 * governance_risk(i) + &
                        0.18d0 * technical_risk(i) + &
                        0.22d0 * equity_risk(i) + &
                        0.13d0 * financial_risk(i)

    values(i) = 0.20d0 * adoption(i) + &
                0.18d0 * operations(i) + &
                0.18d0 * durability(i) + &
                0.15d0 * governance(i) + &
                0.14d0 * equity(i) + &
                0.10d0 * finance(i) - &
                0.05d0 * composite_risk(i)
  end do

  call sort_desc(names, values, composite_risk, n)

  print '(a)', 'rank,intervention,implementation_value,composite_risk'
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

end program implementation_value_model
