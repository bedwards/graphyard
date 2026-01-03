# Blood Money: Detailed Chapter Outline

**Target Length**: 135,000+ words (~11 hours reading at 200 wpm)
**Charts**: 65+ data visualizations

---

## Opening: The Receipt

*~3,000 words, 2 charts*

The book opens with a single image: the author's 2024 tax return. From the gross numbers, we trace exactly where the money went. Of the federal taxes paid, 24 cents of every dollar went to the Pentagon and military. But that line item obscures more than it reveals.

This opening chapter asks the question that drives the entire book: If we could trace every dollar from a median taxpayer's pocket through the federal apparatus to its final destination—including destinations the government would rather not acknowledge—what would we find? How many deaths did your taxes pay for last year? How does that compare to your parents' taxes, or your grandparents'?

The chapter establishes the methodology: we're going to calculate, with as much precision as the data allows, the "body count per taxpayer" for different countries and eras. The number will never be exact. But it will be grounded in the best available evidence.

**Charts:**
1. `ch00-tax-breakdown-2024` - BAR - Federal tax dollar breakdown showing military vs. other spending
2. `ch00-historical-milex-share` - LINE - Military spending as % of federal budget, 1940-2025

---

## Part I: The Price of Power (Historical Survey)

*~50,000 words, 25 charts*

### Chapter 1: The Accounting of Death

*~8,000 words, 4 charts*

Before we can calculate what citizens paid for atrocities, we must grapple with a fundamental problem: how do we count the dead?

This chapter surveys the major datasets and methodologies. The Uppsala Conflict Data Program counts battle deaths differently than Rummel's democide statistics. The Political Terror Scale measures state repression on an ordinal scale, not in bodies. Each approach captures something real while missing something else.

We present the key distinctions that will structure our analysis throughout the book:

**Direct vs. Indirect Deaths**: The bomb that kills a family is direct. The destroyed hospital that means a treatable illness becomes fatal is indirect. Brown University's Costs of War project estimates 3.6-3.7 million indirect deaths from post-9/11 wars, versus 940,000 direct deaths. Should a taxpayer feel equally complicit in both?

**Military vs. Civilian Deaths**: Just war theory holds that killing enemy combatants in legitimate war is morally permissible. Absolute pacifists reject this distinction. We present both frameworks and let readers apply their preferred lens to the data.

**Intentional vs. Incidental**: The Holocaust was targeted extermination. Hiroshima was intended to end a war. Drone strikes aim at militants but kill bystanders. The moral weight differs, but the dead are equally dead.

**State vs. Non-State Violence**: We focus primarily on state violence because that's what taxes fund. But we acknowledge the fuzzy boundary when states fund militias, paramilitaries, and proxy forces.

The chapter ends by establishing our default methodology: we will calculate both "conservative" estimates (direct civilian deaths only, attributable to official state forces) and "inclusive" estimates (all deaths including indirect, including combatants, including proxy forces). Readers can choose which moral framework to apply.

**Charts:**
1. `ch01-deaths-by-type-20c` - STACKED BAR - 20th century deaths by type: genocide, war (combatant), war (civilian), other democide
2. `ch01-ucdp-vs-rummel` - SCATTER - Comparison of UCDP vs Rummel estimates for overlapping events
3. `ch01-direct-indirect-ratio` - HORIZONTAL BAR - Ratio of indirect to direct deaths in major conflicts
4. `ch01-death-counting-methods` - TABLE/DIAGRAM - Methodological approaches compared

---

### Chapter 2: The Median Citizen Through History

*~7,000 words, 3 charts*

What did it mean to be a "median income" citizen in different eras? This chapter reconstructs the economic reality of typical citizens across our case studies.

We draw on the Maddison Project's historical GDP data, supplemented by economic historians' work on income distribution. A British factory worker in 1857 earned roughly £50/year—perhaps $5,000 in today's purchasing power. A Soviet collective farmer in 1937 had nominal rubles that meant little in a shortage economy. An American autoworker in 1968 enjoyed purchasing power that many 2025 Americans would envy.

The tax burden varied enormously. Medieval peasants paid perhaps 10% in direct taxes but faced endless other exactions. Victorian Britain's income tax was 3% for middle incomes. The United States in World War II extracted 23% of GDP in taxes. Modern Denmark takes 46%.

We establish a standardized metric: **Median Taxpayer Military Contribution (MTMC)**—the amount a median-income citizen paid toward military and security spending, expressed in constant 2020 international dollars. This becomes our denominator for calculating "cost per death."

**Charts:**
1. `ch02-median-income-historical` - LINE (multi-series) - Median income (2020 PPP USD) for key countries 1800-2020
2. `ch02-tax-burden-historical` - LINE (multi-series) - Effective tax rate for median citizens 1800-2020
3. `ch02-mtmc-comparison` - HORIZONTAL BAR - Median Taxpayer Military Contribution by country-era

---

### Chapter 3: The Colonial Balance Sheet

*~9,000 words, 4 charts*

European colonialism represents history's largest sustained program of state violence against civilians. From the Belgian Congo to British India, from German Southwest Africa to the French suppression of Algeria, European taxpayers financed centuries of extraction, exploitation, and extermination.

This chapter attempts the difficult task of quantifying colonial deaths and allocating responsibility to metropolitan taxpayers. We focus on three detailed case studies:

**Belgian Congo (1885-1908)**: Under Leopold II's personal rule, the population declined by an estimated 1-10 million. Belgian metropolitan taxpayers didn't directly fund the Congo Free State, but the Belgian state took over in 1908. What was the taxpayer cost per death?

**British India (1757-1947)**: The famines alone—1770, 1876-78, 1943—killed tens of millions. How do we account for deaths caused by policy (export of grain during famine) versus deaths from neglect versus deaths from direct violence?

**German Southwest Africa (1904-1908)**: The Herero and Nama genocide killed 65,000-100,000 in a deliberate extermination campaign. German taxpayers funded the Schutztruppe. We can calculate the cost per death with unusual precision.

The chapter grapples with the problem of indirect colonial violence: deaths from disease, famine, and exploitation that wouldn't have occurred absent colonial rule. These numbers dwarf direct killing but are harder to attribute.

**Charts:**
1. `ch03-colonial-deaths-map` - CHOROPLETH - Estimated colonial deaths by territory
2. `ch03-congo-population` - LINE - Congo population estimates 1880-1920
3. `ch03-german-swa-spending` - BAR - German military spending on Southwest Africa campaign
4. `ch03-british-india-famines` - BAR - Death tolls of major British India famines

---

### Chapter 4: The Totalitarian Century

*~10,000 words, 5 charts*

The 20th century was history's bloodiest. States killed more of their own citizens than died in all the century's wars combined. Drawing heavily on Rummel's democide data and UCDP conflict records, we analyze the worst offenders.

**The Soviet Union (1917-1991)**: Rummel estimates 62 million deaths—from the Civil War through collectivization, the Gulag, the Terror, and beyond. What did the average Soviet citizen contribute to this killing apparatus? The USSR's command economy complicates our tax analysis, but we estimate the share of national output devoted to internal security.

**Nazi Germany (1933-1945)**: The Holocaust killed 6 million Jews plus 5-6 million others (Roma, disabled, Soviet POWs, political prisoners). The German taxpayer financed a war machine that consumed 70% of GDP at its peak. We calculate the per-taxpayer cost of genocide.

**Maoist China (1949-1976)**: The Great Leap Forward caused 15-55 million famine deaths. The Cultural Revolution killed 500,000-2 million more. These were state policies, but were they funded the way military killing is funded? We examine the economics of politically-induced famine.

**Other 20th Century Democides**: Brief surveys of Cambodia (1.7-2.5 million), Indonesia (500,000-1 million), and other major episodes.

The chapter calculates our first set of rankings: deaths per median taxpayer dollar across totalitarian regimes. The results are sobering: some regimes achieved extraordinary killing efficiency precisely because they were poor.

**Charts:**
1. `ch04-20c-democide-treemap` - TREEMAP - 20th century democide deaths by regime
2. `ch04-soviet-repression-timeline` - LINE - Soviet political deaths by year 1917-1991
3. `ch04-nazi-war-spending` - STACKED AREA - Nazi Germany spending by category 1933-1945
4. `ch04-china-glf-mortality` - LINE - China mortality rates during Great Leap Forward
5. `ch04-totalitarian-deaths-per-dollar` - HORIZONTAL BAR - Deaths per median taxpayer dollar by regime

---

### Chapter 5: Cold War Shadows

*~8,000 words, 4 charts*

The Cold War saw superpowers fight indirectly, funding proxy wars and covert operations across the globe. American and Soviet taxpayers financed violence they often didn't know about until decades later.

**Guatemala (1954-1996)**: The CIA-backed coup of 1954 began four decades of civil war and genocide that killed 200,000. American taxpayers funded the initial operation and subsequent military aid. We trace the money.

**Indonesia (1965-1966)**: The anti-communist massacres killed 500,000-1 million. The US role remains debated, but CIA support for the military is documented. What did American taxpayers contribute to this killing?

**Chile (1973-1990)**: Operation Condor and Pinochet's dictatorship. The CIA's documented role. Taxpayer funding of repression.

**El Salvador (1979-1992)**: $4 billion in US military aid during a civil war with 75,000 deaths, including the El Mozote massacre by US-trained troops.

**Afghanistan (1979-1989)**: The US funded mujahideen resistance to Soviet occupation. The Soviets lost 15,000 soldiers; Afghan deaths exceeded one million. Both superpowers' taxpayers financed this bloodbath.

The chapter calculates the hidden cost: what American and Soviet taxpayers paid for Cold War covert operations and proxy wars.

**Charts:**
1. `ch05-cold-war-proxy-map` - MAP - Cold War proxy conflicts and death tolls
2. `ch05-cia-budget-historical` - LINE - Estimated CIA/intelligence budget 1947-2024
3. `ch05-guatemala-deaths-timeline` - LINE - Guatemala conflict deaths 1960-1996
4. `ch05-us-military-aid-latin-america` - STACKED AREA - US military aid to Latin America 1950-1990

---

### Chapter 6: Wars of Choice

*~8,000 words, 5 charts*

The post-Cold War era saw the United States engage in a series of military interventions with varying justifications. The Gulf War, Kosovo, Afghanistan, Iraq, Libya, Syria, Yemen—each with distinct death tolls and taxpayer costs.

This chapter applies our methodology to post-1990 American military action:

**Gulf War (1991)**: 20,000-35,000 Iraqi military deaths, perhaps 3,500 civilians. Cost: $61 billion. A relatively "clean" conventional war by historical standards.

**Afghanistan (2001-2021)**: 176,000+ total deaths including 46,000+ civilians. Cost: $2.3 trillion. Two decades of grinding conflict.

**Iraq (2003-2011+)**: 185,000-208,000 violent deaths documented; total excess mortality estimates range from 400,000 to 1 million+. Cost: $2 trillion+. The most controversial American war since Vietnam.

**Drone warfare (2004-present)**: Bureau of Investigative Journalism documents thousands of strikes across multiple countries. Often conducted outside declared war zones.

We calculate year-by-year costs and deaths, building toward Part II's detailed American analysis.

**Charts:**
1. `ch06-us-wars-cost-deaths` - SCATTER - US post-1990 conflicts: cost vs. death toll
2. `ch06-iraq-casualties-timeline` - LINE - Iraq conflict deaths by year 2003-2020
3. `ch06-afghanistan-timeline` - LINE - Afghanistan conflict deaths by year 2001-2021
4. `ch06-drone-strikes-map` - MAP - Drone strikes by location and casualty count
5. `ch06-post-911-cumulative` - STACKED AREA - Cumulative post-9/11 war deaths by conflict

---

## Part II: American Reckoning (1975-2025)

*~40,000 words, 20 charts*

### Chapter 7: A Life in Taxes

*~5,000 words, 3 charts*

The author was born in 1975 in Waco, Texas. This chapter establishes the personal frame: what it meant to grow up as an American taxpayer during these five decades.

We construct the "Taxpayer Biography"—year-by-year median income, effective tax rate, and military spending contribution from 1975 to 2025. At what age did Brian first pay taxes? How has the real burden changed?

The chapter integrates economic data with personal memory: the Reagan defense buildup during high school, the Gulf War during college, 9/11 as an adult, the long war on terror during middle age.

**Charts:**
1. `ch07-median-income-1975-2025` - LINE - Real median household income 1975-2025
2. `ch07-effective-tax-rate-1975-2025` - LINE - Median effective federal tax rate 1975-2025
3. `ch07-cumulative-taxes-paid` - AREA - Cumulative lifetime taxes at median income

---

### Chapter 8: The End of Vietnam (1975-1980)

*~6,000 words, 3 charts*

The year of the author's birth was the year Saigon fell. American combat deaths had ended, but the consequences continued.

**Vietnam aftermath**: Boat people, reeducation camps, Cambodian genocide (itself partly a consequence of US bombing). The war that defined a generation was over, but its shadow persisted.

**Cold War steady state**: Carter administration, CIA operations, military spending at post-Vietnam lows. This was the "peace dividend" era before Reagan.

**Iran and Afghanistan**: The 1979 upheavals that would shape the next four decades. The embassy hostage crisis. The Soviet invasion.

The chapter calculates: what did the median 1975-1980 taxpayer contribute to violence? These were relatively quiet years for American military action, but the covert apparatus remained active.

**Charts:**
1. `ch08-vietnam-total-deaths` - BAR - Vietnam War death toll by category
2. `ch08-milex-1970s` - LINE - US military spending 1970-1980 (constant dollars)
3. `ch08-cold-war-proxy-deaths-1970s` - BAR - Deaths in Cold War proxy conflicts 1975-1980

---

### Chapter 9: The Reagan Buildup (1981-1988)

*~6,000 words, 3 charts*

Military spending nearly doubled under Reagan. The Cold War entered its final, most expensive phase. Where did all that money go—and who died because of it?

**Central America**: El Salvador, Nicaragua, Guatemala. The dirty wars of the 1980s. Death squads and Contras. US military aid funding atrocities.

**Lebanon**: The 1983 barracks bombing killed 241 American servicemembers. The intervention cost lives on all sides.

**Grenada, Libya**: Small military actions with limited casualties.

**The arms race**: Most Reagan military spending went to weapons never fired. But the opportunity cost was real—those billions could have addressed other priorities.

The chapter examines whether unfired weapons count in our moral ledger. The pacifist says yes; the just war theorist might disagree.

**Charts:**
1. `ch09-reagan-milex-buildup` - LINE - Military spending 1980-1989 with Reagan term highlighted
2. `ch09-central-america-deaths` - STACKED BAR - Central American conflict deaths by country 1980-1992
3. `ch09-us-military-aid-1980s` - BAR - US military aid recipients 1980-1988

---

### Chapter 10: Peace Dividend? (1989-2000)

*~5,000 words, 3 charts*

The Cold War ended. Military spending declined. But American forces saw action in Panama, the Gulf, Somalia, Haiti, the Balkans.

**Panama (1989)**: Perhaps 3,000 deaths in the invasion to capture Noriega.

**Gulf War (1991)**: The first major post-Cold War conflict. A success by conventional military metrics, but thousands of Iraqi civilians died.

**Somalia (1992-1994)**: Humanitarian intervention turned deadly. Black Hawk Down.

**Haiti (1994)**: Intervention with minimal casualties.

**Balkans (1995-1999)**: Bosnia and Kosovo. NATO air campaigns. Relatively few US casualties; Serb and Kosovar civilians paid a higher price.

This was the era of "humanitarian intervention"—using military force for ostensibly good ends. The chapter examines whether the death toll justifies the label.

**Charts:**
1. `ch10-peace-dividend-milex` - LINE - Military spending 1988-2000 (the peace dividend)
2. `ch10-1990s-conflicts-deaths` - HORIZONTAL BAR - US military action death tolls 1989-2000
3. `ch10-balkans-casualties` - STACKED BAR - Balkans intervention casualties by category

---

### Chapter 11: The Forever War Begins (2001-2008)

*~7,000 words, 4 charts*

September 11, 2001 killed nearly 3,000 Americans. The response would kill hundreds of thousands more, mostly not American.

**Afghanistan**: The Taliban fell quickly. Then came the long insurgency. By 2025, over 176,000 would be dead.

**Iraq**: The 2003 invasion based on false WMD claims. "Mission Accomplished" preceded years of chaos. Sectarian violence killed civilians by the tens of thousands.

**Detention and torture**: Abu Ghraib, Guantanamo, black sites. The taxpayer funded torture.

**Surveillance state**: The NSA's domestic and international surveillance. The erosion of civil liberties.

This chapter calculates the surge in taxpayer-funded violence. The median American's military contribution rose sharply. The death toll followed.

**Charts:**
1. `ch11-post-911-milex-surge` - LINE - Military spending 2000-2010 with 9/11 marked
2. `ch11-afghanistan-iraq-deaths-cumulative` - LINE (dual axis) - Cumulative deaths in Afghanistan and Iraq
3. `ch11-iraq-civilian-deaths-by-year` - BAR - Iraqi civilian deaths by year 2003-2008
4. `ch11-detention-population` - LINE - Guantanamo and other detention populations over time

---

### Chapter 12: Drones and Distance (2009-2016)

*~6,000 words, 3 charts*

The Obama era saw a partial drawdown from Iraq but an expansion of drone warfare and special operations. The taxpayer paid for killing that happened mostly out of sight.

**Drone warfare**: Thousands of strikes in Pakistan, Yemen, Somalia, Libya. The Bureau of Investigative Journalism documents the casualties, including civilians.

**Libya (2011)**: The intervention that toppled Gaddafi and created a failed state. NATO air power killed combatants and civilians.

**Syria (2011-present)**: The civil war that drew in multiple powers. US bombing against ISIS. Russian bombing for Assad.

**The pivot**: Military spending declined from Iraq War peaks but remained far above pre-9/11 levels.

This chapter examines the moral weight of remote-control killing. Does distance diminish culpability?

**Charts:**
1. `ch12-drone-strikes-by-year` - BAR - CIA and military drone strikes by year and country
2. `ch12-drone-casualties-breakdown` - STACKED BAR - Drone strike casualties: militants vs. civilians vs. unknown
3. `ch12-milex-obama-era` - LINE - Military spending 2008-2016

---

### Chapter 13: America First? (2017-2024)

*~5,000 words, 3 charts*

The Trump and Biden years saw shifting priorities but continued violence.

**Yemen**: The Saudi-led intervention, backed by US weapons and intelligence. Tens of thousands dead; millions facing famine.

**Afghanistan withdrawal**: The chaotic 2021 exit after 20 years of war. The return of the Taliban. The final costs tallied.

**Ukraine**: US military aid in a proxy war with Russia. No American combat deaths, but billions in weapons.

**Gaza (2023-present)**: The Hamas attack and Israeli response. US weapons and diplomatic support. Tens of thousands of Palestinian civilians dead.

This chapter brings us to the present: what is the median taxpayer funding right now?

**Charts:**
1. `ch13-yemen-casualties-timeline` - LINE - Yemen conflict deaths 2015-2024
2. `ch13-us-military-aid-ukraine` - BAR - US military aid to Ukraine by fiscal year
3. `ch13-gaza-casualties-2023-24` - BAR - Gaza casualties October 2023-present

---

### Chapter 14: The Fifty-Year Ledger

*~5,000 words, 5 charts*

The culminating chapter of Part II: fifty years of American taxpayer-funded violence, summed up.

We present the complete data series: year by year from 1975 to 2025, the median taxpayer's military contribution and the attributed death toll. Which years were worst? The answer depends on your ethical framework.

By civilian deaths directly caused, the worst years cluster around the Iraq War (2003-2007) and recent conflicts.

By total deaths including combatants, the pattern shifts.

By cost-per-death, some years were remarkably "efficient" in their killing; others spent vast sums for limited violence.

We present the cumulative total: over fifty years, the median American taxpayer has contributed approximately $X to military spending, during a period when American military action killed approximately Y people. The implied cost-per-death and taxpayer-share-per-death are sobering.

**Charts:**
1. `ch14-50-year-timeline` - LINE (dual axis) - Median MTMC and attributed deaths 1975-2025
2. `ch14-worst-years-ranking` - HORIZONTAL BAR - Years ranked by deaths per taxpayer dollar
3. `ch14-cumulative-deaths-stacked` - STACKED AREA - Cumulative deaths by conflict 1975-2025
4. `ch14-cost-per-death-trend` - LINE - Cost per attributed death over time
5. `ch14-taxpayer-share-per-death` - LINE - Median taxpayer's share of each death over time

---

## Part III: The Economics of Violence

*~30,000 words, 15 charts*

### Chapter 15: Cheap Death

*~8,000 words, 4 charts*

Rwanda's genocide killed 800,000+ people in 100 days. The weapons were mostly machetes—total arms imports were about $112 million. The cost per death was roughly $140.

The Holocaust required a vast bureaucratic apparatus, dedicated rail networks, purpose-built camps. Still, the Nazis achieved industrialized murder at horrific scale.

This chapter examines the economics of low-budget mass killing:

**The machete question**: Simple tools enable massacres. Rwanda proves technology isn't required for genocide.

**Militia and paramilitaries**: Cheaper than standing armies. Used by governments seeking deniability.

**Starvation as weapon**: The cheapest killing requires only policy decisions—block food aid, divert harvests, enforce export quotas.

**Political mobilization**: The Khmer Rouge turned an entire society into killing machine and victims simultaneously.

We calculate deaths-per-dollar for low-budget atrocities and compare to high-tech warfare.

**Charts:**
1. `ch15-rwanda-killing-rate` - LINE - Rwanda genocide deaths per day over 100 days
2. `ch15-low-budget-atrocities` - SCATTER - Death toll vs. documented military spending
3. `ch15-cost-per-death-comparison` - HORIZONTAL BAR - Cost per death across different atrocities
4. `ch15-weapon-type-deaths` - TREEMAP - 20th century atrocity deaths by weapon type

---

### Chapter 16: Expensive Destruction

*~7,000 words, 3 charts*

A single Tomahawk cruise missile costs $2 million. A B-2 bomber mission costs $100,000+ per hour. Modern warfare is staggeringly expensive per kill.

**Precision warfare**: The US military claims to minimize civilian casualties through precision weapons. The data suggest precision is relative.

**The $85,000 toilet seat problem**: Military procurement is notoriously inefficient. Does waste reduce moral culpability?

**Contractor costs**: Mercenaries and military contractors consume vast budgets. Blackwater operatives earned more than generals.

**Reconstruction and occupation**: The costs extend far beyond combat. Building (and rebuilding) infrastructure. Training local forces. Nation-building that often fails.

We calculate the full cost per death for modern American military action, including all overhead.

**Charts:**
1. `ch16-weapon-costs` - HORIZONTAL BAR - Cost of major weapon systems
2. `ch16-us-cost-per-death-overtime` - LINE - Estimated US military cost per attributed death 1950-2024
3. `ch16-iraq-spending-breakdown` - STACKED BAR - Iraq War spending by category

---

### Chapter 17: The Comparison Problem

*~7,000 words, 4 charts*

How do we compare the moral weight of a $2 million missile strike that kills a family of four versus a $5 machete attack that does the same? This chapter engages the philosophy directly.

**Intentionality arguments**: Does it matter that the missile was aimed at a militant while the machete was wielded against identified victims?

**Scale arguments**: Machetes killed more in Rwanda than missiles have killed in Yemen. Does scale outweigh technology?

**Wealth arguments**: A poor country spending $112 million on genocide is making a larger sacrifice than a rich country spending $1 trillion on war. Should we normalize by GDP?

**The taxpayer's moral distance**: The American paying taxes has even less direct involvement than the soldier firing the missile or the Interahamwe swinging the machete. Does distance diminish culpability?

We develop a framework for cross-context comparison that accounts for wealth, scale, intentionality, and taxpayer remove. No framework is perfect; we present multiple and let readers choose.

**Charts:**
1. `ch17-deaths-per-gdp-pct` - SCATTER - Deaths caused vs. military spending as % of GDP
2. `ch17-intentionality-spectrum` - DIAGRAM - Types of killing from targeted to incidental
3. `ch17-moral-distance-framework` - DIAGRAM - Layers of moral responsibility
4. `ch17-normalized-comparison` - HORIZONTAL BAR - Atrocities ranked by various normalization schemes

---

### Chapter 18: State Violence on a Budget

*~8,000 words, 4 charts*

Many of history's worst regimes were poor. Stalin's USSR, Mao's China, Pol Pot's Cambodia—these weren't wealthy societies devoting vast resources to killing. They achieved mass death through political mobilization, not military spending.

This chapter examines what we might call "death efficiency"—the ability of regimes to kill many people without expensive military apparatus:

**Terror as multiplier**: A small secret police can cow millions through selective violence. The Stasi employed 90,000 people to suppress 17 million.

**Self-enforcement**: The Cultural Revolution turned citizens into informers and enforcers. No external army was required.

**Indirect killing**: Famine policies kill without bullets. The Holodomor was Stalin's cheapest genocide.

**Opportunity cost**: Poor countries that spend on violence forgo development. The hidden cost compounds the direct death toll.

We calculate that the poorest regimes often achieved the highest deaths-per-dollar, but this efficiency came at immense cost to their own populations' welfare.

**Charts:**
1. `ch18-gdp-vs-democide` - SCATTER - GDP per capita vs. democide deaths for 20th century regimes
2. `ch18-killing-efficiency` - HORIZONTAL BAR - Deaths per million dollars of military spending
3. `ch18-indirect-death-comparison` - BAR - Direct vs. indirect deaths for major atrocities
4. `ch18-development-counterfactual` - LINE - Estimated development foregone due to state violence spending

---

## Part IV: The Moral Ledger

*~15,000 words, 5 charts*

### Chapter 19: What Do We Owe?

*~5,000 words, 1 chart*

Having established the data, we turn to moral philosophy. What responsibility does the taxpayer bear for state violence?

**Just war theory response**: The taxpayer is not directly culpable for legitimate military action. Only violations of jus in bello (targeting civilians, disproportionate force) implicate the citizenry, and even then, individual soldiers bear primary responsibility.

**Pacifist response**: All war is wrong; all funding of war is wrong. The taxpayer who pays is complicit in every death.

**Democratic responsibility**: Citizens of democracies have more responsibility than subjects of autocracies. We chose our leaders; we fund the military through representatives.

**Structural responsibility**: Perhaps the question isn't individual guilt but collective obligation to change the system.

We don't resolve these debates. We present each framework and let the data speak through each lens.

**Chart:**
1. `ch19-responsibility-frameworks` - DIAGRAM - Ethical frameworks and their implications for taxpayer responsibility

---

### Chapter 20: The Possibility of Change

*~5,000 words, 2 charts*

Throughout history, citizens have resisted funding state violence. War tax resistance, conscientious objection, political organizing—people have tried to break the chain between their taxes and death.

**War tax resistance**: From Quakers in 1755 to Vietnam-era resisters to modern-day refusers. The practical challenges of refusing to fund war.

**Political action**: Movements that have actually reduced state violence. The nuclear freeze movement. Anti-war protests.

**Transparency and accountability**: Sunshine laws, declassification, investigative journalism. Knowing what our taxes fund is the first step to changing it.

**Democratic leverage**: In democracies, citizens have the power to elect leaders who will fund less violence. Have we used that power?

**Charts:**
1. `ch20-war-tax-resistance-timeline` - LINE - War tax resistance incidents over time
2. `ch20-public-opinion-vs-military-action` - SCATTER - Public support for wars vs. continuation

---

### Chapter 21: The Ledger

*~5,000 words, 2 charts*

The final chapter presents the complete analysis in summary form.

For the historical survey: which country-era combinations produced the worst outcomes for median taxpayers? The answer depends on your framework, but some patterns emerge.

For the American experience: fifty years of data show ebbs and flows in taxpayer-funded violence, but no decade was clean.

For the economics of violence: rich countries spend more per death, but that doesn't make their killing more moral.

We present the ultimate table: every major atrocity since 1800, with estimated death toll, estimated cost, implied cost per death, and median taxpayer contribution. It is a grim ledger.

The book closes with a question rather than an answer: knowing what we now know, what do we do?

**Charts:**
1. `ch21-comprehensive-ranking` - HORIZONTAL BAR - All major atrocities ranked by deaths per taxpayer dollar
2. `ch21-final-summary-table` - TABLE - Complete data for all analyzed atrocities

---

## Appendices

### Appendix A: Data Sources and Methodology

Complete documentation of all data sources, transformations, and calculations.

### Appendix B: Complete Data Tables

Full year-by-year data for all country-years analyzed.

### Appendix C: Uncertainty and Limitations

Discussion of what we don't know and why estimates should be treated with appropriate caution.

### Appendix D: Bibliography

Complete references.

---

## Chart Manifest Summary

| Part | Chapters | Charts |
|------|----------|--------|
| Opening | 1 | 2 |
| Part I: Historical | 6 | 25 |
| Part II: American | 8 | 23 |
| Part III: Economics | 4 | 15 |
| Part IV: Moral | 3 | 5 |
| **Total** | **22** | **70** |

---

*Last updated: January 2026*
