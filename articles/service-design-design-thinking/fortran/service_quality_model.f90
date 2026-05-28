program service_quality_model
  implicit none

  integer, parameter :: n = 10
  character(len=128) :: names(n)
  real(8) :: p(n), clarity(n), trust(n), accessibility(n), user_burden(n)
  real(8) :: staff_load(n), recovery(n), quality(n), priority(n)
  real(8) :: reliability
  integer :: i

  names = [ character(len=128) :: &
    "Discover Service", &
    "Understand Eligibility", &
    "Prepare Documents", &
    "Submit Request", &
    "Wait for Review", &
    "Receive Decision", &
    "Resolve Issue", &
    "Maintain Access", &
    "Renew Service", &
    "Exit or Transition" ]

  p = [0.92d0, 0.78d0, 0.70d0, 0.84d0, 0.76d0, 0.88d0, 0.62d0, 0.80d0, 0.74d0, 0.82d0]
  clarity = [7.4d0, 5.8d0, 5.2d0, 6.8d0, 5.5d0, 6.4d0, 5.0d0, 6.2d0, 5.9d0, 6.0d0]
  trust = [7.0d0, 5.8d0, 5.4d0, 6.4d0, 5.3d0, 6.2d0, 5.5d0, 6.0d0, 5.7d0, 6.1d0]
  accessibility = [7.2d0, 5.6d0, 5.0d0, 6.8d0, 5.4d0, 6.0d0, 5.8d0, 6.4d0, 5.8d0, 6.0d0]
  user_burden = [3.5d0, 5.8d0, 7.4d0, 6.2d0, 6.8d0, 5.6d0, 7.2d0, 5.9d0, 6.5d0, 5.4d0]
  staff_load = [3.0d0, 5.2d0, 6.0d0, 5.8d0, 6.5d0, 5.6d0, 7.4d0, 6.2d0, 6.4d0, 5.2d0]
  recovery = [6.8d0, 5.4d0, 4.8d0, 5.8d0, 4.6d0, 5.2d0, 5.0d0, 5.6d0, 5.0d0, 5.8d0]

  reliability = 1.0d0

  do i = 1, n
    quality(i) = 0.22d0 * p(i) * 10.0d0 + &
                 0.18d0 * clarity(i) + &
                 0.18d0 * trust(i) + &
                 0.16d0 * accessibility(i) + &
                 0.14d0 * recovery(i) - &
                 0.07d0 * user_burden(i) - &
                 0.05d0 * staff_load(i)

    priority(i) = 0.34d0 * (1.0d0 - p(i)) * 10.0d0 + &
                  0.26d0 * (0.55d0 * user_burden(i) + 0.45d0 * staff_load(i)) + &
                  0.18d0 * (10.0d0 - clarity(i)) + &
                  0.12d0 * (10.0d0 - accessibility(i)) + &
                  0.10d0 * (10.0d0 - recovery(i))

    reliability = reliability * p(i)
  end do

  call sort_desc(names, quality, priority, p, n)

  print '(a,f10.8)', 'end_to_end_reliability,', reliability
  print '(a)', 'rank,stage,service_stage_quality,redesign_priority,completion_probability'
  do i = 1, n
    print '(i0,a,a,a,f8.4,a,f8.4,a,f8.4)', i, ',', trim(names(i)), ',', quality(i), ',', priority(i), ',', p(i)
  end do

contains

  subroutine sort_desc(names, quality, priority, p, n)
    integer, intent(in) :: n
    character(len=128), intent(inout) :: names(n)
    real(8), intent(inout) :: quality(n), priority(n), p(n)
    integer :: i, j
    real(8) :: temp_quality, temp_priority, temp_p
    character(len=128) :: temp_name

    do i = 1, n - 1
      do j = i + 1, n
        if (priority(j) > priority(i)) then
          temp_priority = priority(i)
          priority(i) = priority(j)
          priority(j) = temp_priority

          temp_quality = quality(i)
          quality(i) = quality(j)
          quality(j) = temp_quality

          temp_p = p(i)
          p(i) = p(j)
          p(j) = temp_p

          temp_name = names(i)
          names(i) = names(j)
          names(j) = temp_name
        end if
      end do
    end do
  end subroutine sort_desc

end program service_quality_model
