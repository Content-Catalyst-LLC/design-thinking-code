program institutional_readiness_model
  implicit none

  integer, parameter :: n = 10
  character(len=180) :: names(n)
  real(8) :: desirability(n), authority(n), capability(n), funding(n), policy_fit(n)
  real(8) :: governance(n), trust_gain(n), burden_reduction(n), coordination(n), risk(n)
  real(8) :: data_readiness(n), frontline_fit(n), maintenance(n), equity(n), public_value(n)
  real(8) :: readiness(n), absorption(n), public_priority(n), sequencing(n), portfolio(n)
  integer :: i

  names = [ character(len=180) :: &
    "Simplify eligibility pathway", &
    "Create assisted access model", &
    "Redesign cross-department handoffs", &
    "Build institutional learning dashboard", &
    "Prototype community accountability board", &
    "Modernize legacy case-management data", &
    "Redesign frontline escalation process", &
    "Create AI-assisted research synthesis workflow", &
    "Develop burden audit and repair pathway", &
    "Create policy interpretation review board" ]

  desirability = [8.8d0,9.0d0,8.2d0,7.6d0,8.4d0,7.8d0,8.6d0,7.4d0,8.8d0,7.8d0]
  authority = [6.4d0,6.8d0,5.8d0,7.2d0,5.4d0,6.0d0,7.0d0,6.6d0,6.2d0,5.8d0]
  capability = [6.8d0,6.4d0,5.6d0,7.0d0,5.8d0,5.2d0,7.2d0,6.2d0,6.4d0,5.8d0]
  funding = [6.6d0,6.2d0,5.8d0,6.8d0,5.4d0,5.0d0,6.6d0,6.0d0,6.0d0,5.4d0]
  policy_fit = [6.0d0,6.4d0,6.8d0,7.4d0,5.8d0,7.0d0,7.2d0,6.6d0,6.6d0,7.6d0]
  governance = [6.2d0,6.4d0,5.6d0,7.2d0,5.8d0,6.0d0,7.0d0,6.4d0,6.8d0,6.4d0]
  trust_gain = [8.2d0,8.8d0,7.6d0,6.8d0,9.0d0,6.4d0,7.8d0,6.6d0,8.6d0,7.4d0]
  burden_reduction = [8.6d0,8.4d0,7.4d0,6.2d0,7.8d0,6.8d0,8.0d0,6.4d0,9.0d0,7.6d0]
  coordination = [6.8d0,7.2d0,8.6d0,6.4d0,7.8d0,8.8d0,6.6d0,7.4d0,7.2d0,7.8d0]
  risk = [5.8d0,6.2d0,7.4d0,5.6d0,6.8d0,8.0d0,5.4d0,6.6d0,6.0d0,6.8d0]
  data_readiness = [6.0d0,5.8d0,6.2d0,7.4d0,5.6d0,5.4d0,6.8d0,7.0d0,6.2d0,6.0d0]
  frontline_fit = [6.8d0,7.0d0,6.0d0,6.6d0,6.0d0,5.4d0,8.0d0,6.2d0,7.0d0,6.2d0]
  maintenance = [6.2d0,6.4d0,5.8d0,6.8d0,5.6d0,5.0d0,7.0d0,6.4d0,6.6d0,5.8d0]
  equity = [8.4d0,9.0d0,7.6d0,6.8d0,9.2d0,7.2d0,7.8d0,6.8d0,9.0d0,8.0d0]
  public_value = [8.8d0,9.0d0,8.0d0,7.4d0,8.6d0,7.6d0,8.4d0,7.2d0,8.8d0,8.2d0]

  do i = 1, n
    readiness(i) = 0.14d0*desirability(i) + 0.13d0*authority(i) + &
                   0.12d0*capability(i) + 0.10d0*funding(i) + &
                   0.10d0*policy_fit(i) + 0.11d0*governance(i) + &
                   0.08d0*trust_gain(i) + 0.08d0*burden_reduction(i) + &
                   0.06d0*data_readiness(i) + 0.05d0*frontline_fit(i) + &
                   0.03d0*maintenance(i) - 0.05d0*coordination(i) - 0.05d0*risk(i)

    absorption(i) = 0.18d0*authority(i) + 0.18d0*capability(i) + &
                    0.14d0*funding(i) + 0.14d0*governance(i) + &
                    0.12d0*policy_fit(i) + 0.10d0*frontline_fit(i) + &
                    0.08d0*maintenance(i) + 0.06d0*data_readiness(i)

    public_priority(i) = 0.24d0*public_value(i) + 0.20d0*burden_reduction(i) + &
                         0.18d0*trust_gain(i) + 0.16d0*equity(i) + &
                         0.12d0*desirability(i) + 0.10d0*policy_fit(i) - &
                         0.08d0*risk(i)

    sequencing(i) = 0.28d0*coordination(i) + 0.24d0*risk(i) + &
                    0.14d0*(10.0d0-authority(i)) + 0.12d0*(10.0d0-capability(i)) + &
                    0.10d0*(10.0d0-funding(i)) + 0.07d0*(10.0d0-maintenance(i)) + &
                    0.05d0*(10.0d0-data_readiness(i))

    portfolio(i) = 0.30d0*readiness(i) + 0.26d0*public_priority(i) + &
                   0.20d0*absorption(i) + 0.10d0*equity(i) + &
                   0.06d0*trust_gain(i) - 0.12d0*sequencing(i) - 0.08d0*risk(i)
  end do

  call sort_desc(names, readiness, absorption, public_priority, sequencing, portfolio, n)

  print '(a)', 'rank,option,change_readiness,absorption_capacity,public_value_priority,sequencing_need,portfolio_score'
  do i = 1, n
    print '(i0,a,a,a,f7.4,a,f7.4,a,f7.4,a,f7.4,a,f7.4)', &
      i, ',', trim(names(i)), ',', readiness(i), ',', absorption(i), ',', public_priority(i), ',', sequencing(i), ',', portfolio(i)
  end do

contains

  subroutine sort_desc(names, readiness, absorption, public_priority, sequencing, portfolio, n)
    integer, intent(in) :: n
    character(len=180), intent(inout) :: names(n)
    real(8), intent(inout) :: readiness(n), absorption(n), public_priority(n), sequencing(n), portfolio(n)
    integer :: i, j
    real(8) :: tr, ta, tp, ts, tpo
    character(len=180) :: tn

    do i = 1, n - 1
      do j = i + 1, n
        if (portfolio(j) > portfolio(i)) then
          tpo = portfolio(i); portfolio(i) = portfolio(j); portfolio(j) = tpo
          tr = readiness(i); readiness(i) = readiness(j); readiness(j) = tr
          ta = absorption(i); absorption(i) = absorption(j); absorption(j) = ta
          tp = public_priority(i); public_priority(i) = public_priority(j); public_priority(j) = tp
          ts = sequencing(i); sequencing(i) = sequencing(j); sequencing(j) = ts
          tn = names(i); names(i) = names(j); names(j) = tn
        end if
      end do
    end do
  end subroutine sort_desc

end program institutional_readiness_model
