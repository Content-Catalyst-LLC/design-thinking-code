program sustainability_value_model
  implicit none

  integer, parameter :: n = 10
  character(len=128) :: names(n)
  real(8) :: usability(n), feasibility(n), ecological(n), circularity(n), equity(n)
  real(8) :: durability(n), risk(n), values(n)
  integer :: i

  names = [ character(len=128) :: &
    "Building Retrofit Service Model", &
    "Reusable Packaging Loop", &
    "Neighborhood Mobility Hub", &
    "Repair and Refurbishment Platform", &
    "Community Solar Enrollment Service", &
    "Circular Procurement Toolkit", &
    "Urban Heat Resilience Network", &
    "Water Reuse Participation Model", &
    "Tenant-Centered Electrification Pathway", &
    "Food Waste Prevention Service" ]

  usability = [8.1d0, 7.6d0, 8.4d0, 7.9d0, 8.2d0, 7.3d0, 8.0d0, 7.7d0, 8.3d0, 8.5d0]
  feasibility = [7.4d0, 7.8d0, 6.9d0, 7.5d0, 7.2d0, 8.1d0, 6.8d0, 7.0d0, 6.7d0, 7.9d0]
  ecological = [8.8d0, 8.5d0, 8.2d0, 8.0d0, 8.7d0, 7.9d0, 8.6d0, 8.1d0, 8.9d0, 8.0d0]
  circularity = [7.9d0, 9.1d0, 7.1d0, 8.8d0, 7.0d0, 8.7d0, 7.2d0, 7.6d0, 7.3d0, 8.2d0]
  equity = [7.6d0, 7.2d0, 8.4d0, 7.8d0, 8.8d0, 7.4d0, 8.7d0, 8.1d0, 9.0d0, 8.0d0]
  durability = [8.0d0, 8.2d0, 7.8d0, 7.9d0, 8.1d0, 8.0d0, 8.4d0, 7.7d0, 8.0d0, 7.8d0]
  risk = [4.1d0, 4.6d0, 5.0d0, 4.2d0, 4.8d0, 3.9d0, 5.1d0, 4.7d0, 5.2d0, 3.8d0]

  do i = 1, n
    values(i) = 0.16d0 * usability(i) + &
                0.16d0 * feasibility(i) + &
                0.24d0 * ecological(i) + &
                0.16d0 * circularity(i) + &
                0.14d0 * equity(i) + &
                0.08d0 * durability(i) - &
                0.06d0 * risk(i)
  end do

  call sort_desc(names, values, risk, n)

  print '(a)', 'rank,concept,sustainability_value,risk'
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

end program sustainability_value_model
