program evaluation_value_model
  implicit none

  integer, parameter :: n = 8
  character(len=96) :: names(n)
  real(8) :: outcome(n), burden(n), equity(n), trust(n), durability(n)
  real(8) :: cost(n), risk(n), penalty(n), values(n)
  integer :: i

  names = [ character(len=96) :: &
    "Status Visibility Service", &
    "Plain-Language Support Guide", &
    "Guided Intake Workflow", &
    "Human Escalation Pathway", &
    "Community Navigation Partnership", &
    "Learning Dashboard", &
    "Evaluation Governance Charter", &
    "Equity Outcome Review Loop" ]

  outcome = [8.1d0, 7.8d0, 8.3d0, 8.0d0, 8.4d0, 7.6d0, 7.4d0, 7.7d0]
  burden = [7.6d0, 8.2d0, 7.8d0, 7.4d0, 8.1d0, 7.2d0, 7.0d0, 7.5d0]
  equity = [7.4d0, 8.0d0, 7.3d0, 8.2d0, 8.7d0, 7.5d0, 8.1d0, 8.8d0]
  trust = [7.8d0, 7.6d0, 7.4d0, 8.3d0, 8.5d0, 7.7d0, 8.0d0, 8.2d0]
  durability = [7.5d0, 8.0d0, 7.6d0, 7.7d0, 7.9d0, 8.2d0, 8.5d0, 8.1d0]
  cost = [4.4d0, 3.6d0, 4.2d0, 4.8d0, 5.1d0, 4.0d0, 3.8d0, 4.3d0]
  risk = [4.2d0, 3.5d0, 4.4d0, 4.1d0, 3.8d0, 3.9d0, 3.6d0, 3.7d0]

  do i = 1, n
    penalty(i) = 0.50d0 * cost(i) + 0.50d0 * risk(i)
    values(i) = 0.24d0 * outcome(i) + &
                0.20d0 * burden(i) + &
                0.20d0 * equity(i) + &
                0.16d0 * trust(i) + &
                0.14d0 * durability(i) - &
                0.06d0 * penalty(i)
  end do

  call sort_desc(names, values, penalty, n)

  print '(a)', 'rank,intervention,evaluation_value,penalty'
  do i = 1, n
    print '(i0,a,a,a,f8.4,a,f8.4)', i, ',', trim(names(i)), ',', values(i), ',', penalty(i)
  end do

contains

  subroutine sort_desc(names, values, penalties, n)
    integer, intent(in) :: n
    character(len=96), intent(inout) :: names(n)
    real(8), intent(inout) :: values(n), penalties(n)
    integer :: i, j
    real(8) :: temp_value, temp_penalty
    character(len=96) :: temp_name

    do i = 1, n - 1
      do j = i + 1, n
        if (values(j) > values(i)) then
          temp_value = values(i)
          values(i) = values(j)
          values(j) = temp_value

          temp_penalty = penalties(i)
          penalties(i) = penalties(j)
          penalties(j) = temp_penalty

          temp_name = names(i)
          names(i) = names(j)
          names(j) = temp_name
        end if
      end do
    end do
  end subroutine sort_desc

end program evaluation_value_model
