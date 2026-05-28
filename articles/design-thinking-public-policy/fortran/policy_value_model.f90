program policy_value_model
  implicit none

  integer, parameter :: n = 10
  character(len=128) :: names(n)
  real(8) :: accessibility(n), feasibility(n), legitimacy(n), equity(n)
  real(8) :: burden_reduction(n), durability(n), risk(n), values(n)
  integer :: i

  names = [ character(len=128) :: &
    "Benefits Application Simplification", &
    "Mobile Community Health Enrollment", &
    "Digital Licensing Renewal Redesign", &
    "School Meals Access Outreach", &
    "Tenant Rights Navigation Service", &
    "Disability Benefit Renewal Redesign", &
    "Climate Resilience Grant Access Pilot", &
    "Small Business Compliance Assistance", &
    "Emergency Benefits Auto-Enrollment", &
    "Public Notices Plain-Language Redesign" ]

  accessibility = [8.9d0, 8.4d0, 7.5d0, 8.7d0, 8.6d0, 8.8d0, 8.1d0, 7.9d0, 8.5d0, 8.3d0]
  feasibility = [8.1d0, 7.2d0, 8.5d0, 7.8d0, 7.0d0, 6.9d0, 6.8d0, 8.2d0, 7.1d0, 8.6d0]
  legitimacy = [8.0d0, 8.6d0, 7.4d0, 8.5d0, 8.7d0, 8.4d0, 8.2d0, 7.8d0, 8.1d0, 8.2d0]
  equity = [8.8d0, 9.1d0, 6.9d0, 8.9d0, 9.0d0, 9.2d0, 8.7d0, 7.5d0, 8.9d0, 8.1d0]
  burden_reduction = [9.0d0, 8.0d0, 7.6d0, 8.4d0, 8.7d0, 9.1d0, 8.3d0, 8.1d0, 9.2d0, 8.5d0]
  durability = [7.8d0, 7.4d0, 8.0d0, 7.6d0, 7.3d0, 7.2d0, 7.1d0, 7.9d0, 7.5d0, 8.2d0]
  risk = [3.2d0, 4.4d0, 3.8d0, 3.5d0, 4.8d0, 5.0d0, 4.9d0, 3.7d0, 5.1d0, 2.9d0]

  do i = 1, n
    values(i) = 0.20d0 * accessibility(i) + &
                0.16d0 * feasibility(i) + &
                0.16d0 * legitimacy(i) + &
                0.20d0 * equity(i) + &
                0.14d0 * burden_reduction(i) + &
                0.08d0 * durability(i) - &
                0.06d0 * risk(i)
  end do

  call sort_desc(names, values, risk, n)

  print '(a)', 'rank,pilot,policy_value,risk'
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

end program policy_value_model
