program public_value_model
  implicit none

  integer, parameter :: n = 10
  character(len=180) :: names(n)
  real(8) :: access(n), equity(n), dignity(n), legitimacy(n), accountability(n)
  real(8) :: outcome_strength(n), sustainability(n), learning(n), feasibility(n), governance(n)
  real(8) :: implementation_risk(n), burden_risk(n), participation(n), community_value(n), repair(n), stewardship(n)
  real(8) :: pv(n), readiness(n), stewardship_need(n), portfolio(n)
  integer :: i

  names = [ character(len=180) :: &
    "Assisted access pathway", &
    "Community-led research council", &
    "Plain-language eligibility redesign", &
    "Mobile outreach and navigation support", &
    "Burden audit and repair protocol", &
    "Public value dashboard", &
    "Participatory budgeting prototype", &
    "AI-assisted public comment synthesis", &
    "Community climate resilience hub", &
    "Mutual aid data cooperative" ]

  access = [8.8d0,7.6d0,8.4d0,9.0d0,8.2d0,6.8d0,7.8d0,6.6d0,8.6d0,7.8d0]
  equity = [8.6d0,9.0d0,8.0d0,8.8d0,9.2d0,7.2d0,8.6d0,7.0d0,8.8d0,8.4d0]
  dignity = [8.4d0,8.8d0,8.6d0,8.2d0,8.8d0,6.8d0,8.0d0,6.6d0,8.4d0,8.2d0]
  legitimacy = [7.8d0,9.2d0,7.6d0,8.0d0,8.6d0,7.4d0,9.0d0,6.8d0,8.6d0,8.8d0]
  accountability = [7.6d0,8.8d0,7.4d0,7.6d0,9.0d0,8.2d0,8.4d0,6.4d0,8.0d0,8.6d0]
  outcome_strength = [8.0d0,7.4d0,7.8d0,8.2d0,8.0d0,7.0d0,7.6d0,6.8d0,8.4d0,7.4d0]
  sustainability = [7.2d0,6.8d0,8.0d0,6.6d0,7.6d0,7.4d0,6.4d0,6.8d0,7.2d0,7.0d0]
  learning = [7.6d0,8.2d0,7.4d0,7.2d0,8.8d0,9.0d0,7.8d0,7.6d0,8.0d0,8.6d0]
  feasibility = [7.2d0,6.2d0,8.0d0,6.6d0,7.0d0,7.6d0,5.8d0,6.8d0,6.4d0,5.8d0]
  governance = [7.0d0,7.4d0,7.2d0,6.6d0,8.0d0,8.2d0,6.8d0,6.2d0,7.2d0,7.0d0]
  implementation_risk = [5.8d0,6.8d0,4.8d0,6.6d0,5.6d0,5.4d0,7.2d0,7.6d0,6.8d0,7.4d0]
  burden_risk = [4.8d0,5.6d0,4.2d0,5.8d0,4.0d0,5.2d0,6.4d0,7.0d0,5.8d0,6.2d0]
  participation = [7.4d0,9.2d0,6.8d0,7.8d0,8.2d0,6.4d0,8.8d0,5.8d0,8.6d0,9.0d0]
  community_value = [8.2d0,9.4d0,7.8d0,8.6d0,9.0d0,7.0d0,9.0d0,6.4d0,9.0d0,9.2d0]
  repair = [7.2d0,7.6d0,7.0d0,7.0d0,8.8d0,7.4d0,7.6d0,5.8d0,7.8d0,8.0d0]
  stewardship = [7.0d0,7.2d0,7.6d0,6.6d0,8.0d0,7.8d0,6.6d0,6.4d0,7.4d0,7.0d0]

  do i = 1, n
    pv(i) = 0.13d0*access(i) + 0.15d0*equity(i) + 0.12d0*dignity(i) + &
            0.12d0*legitimacy(i) + 0.13d0*accountability(i) + &
            0.11d0*outcome_strength(i) + 0.08d0*sustainability(i) + &
            0.07d0*learning(i) + 0.05d0*community_value(i) + 0.04d0*repair(i)

    readiness(i) = 0.30d0*pv(i) + 0.17d0*feasibility(i) + 0.16d0*governance(i) + &
                   0.12d0*learning(i) + 0.10d0*participation(i) + &
                   0.08d0*stewardship(i) + 0.07d0*repair(i) - &
                   0.07d0*implementation_risk(i) - 0.07d0*burden_risk(i)

    stewardship_need(i) = 0.24d0*implementation_risk(i) + 0.22d0*burden_risk(i) + &
                          0.16d0*(10.0d0-governance(i)) + &
                          0.12d0*(10.0d0-sustainability(i)) + &
                          0.10d0*(10.0d0-learning(i)) + &
                          0.08d0*(10.0d0-repair(i)) + &
                          0.08d0*(10.0d0-stewardship(i))

    portfolio(i) = 0.36d0*pv(i) + 0.28d0*readiness(i) + &
                   0.14d0*equity(i) + 0.10d0*community_value(i) + &
                   0.06d0*participation(i) - 0.14d0*stewardship_need(i) - &
                   0.06d0*implementation_risk(i)
  end do

  call sort_desc(names, pv, readiness, stewardship_need, portfolio, n)

  print '(a)', 'rank,intervention,public_value_score,impact_readiness,stewardship_need,portfolio_priority'
  do i = 1, n
    print '(i0,a,a,a,f7.4,a,f7.4,a,f7.4,a,f7.4)', &
      i, ',', trim(names(i)), ',', pv(i), ',', readiness(i), ',', stewardship_need(i), ',', portfolio(i)
  end do

contains

  subroutine sort_desc(names, pv, readiness, stewardship_need, portfolio, n)
    integer, intent(in) :: n
    character(len=180), intent(inout) :: names(n)
    real(8), intent(inout) :: pv(n), readiness(n), stewardship_need(n), portfolio(n)
    integer :: i, j
    real(8) :: tpv, tr, ts, tpo
    character(len=180) :: tn

    do i = 1, n - 1
      do j = i + 1, n
        if (portfolio(j) > portfolio(i)) then
          tpo = portfolio(i); portfolio(i) = portfolio(j); portfolio(j) = tpo
          tpv = pv(i); pv(i) = pv(j); pv(j) = tpv
          tr = readiness(i); readiness(i) = readiness(j); readiness(j) = tr
          ts = stewardship_need(i); stewardship_need(i) = stewardship_need(j); stewardship_need(j) = ts
          tn = names(i); names(i) = names(j); names(j) = tn
        end if
      end do
    end do
  end subroutine sort_desc

end program public_value_model
