Takes rooms, teachers, and courses to create a class schedule. It makes sure there are no conflicts, such as two coursees in the same room, a teacher teaching two coursees at the same time, etc. 

![image](https://github.com/Py-mon/Scheduler/assets/102424561/3e924f19-a2d2-461c-8d80-322dd0d738d1)

New Features:
- To make the course split in half, you can just leave the section blank (See `Bible`, `Science`, etc)

- To make a course during the same period, you can set the `Sections` to `Same`. (See `Gym`)

- You can set courses to only be on certain sections. (See `Chinese` and `Spanish`)
  
- To change the days for different sections, you can duplicate the course, set it to the other section, and change the days. (See `Art` and `Study`)

- To make the course span multiple grades, add the grade to the `Grades`. (See `Band` and `Choir`)


- If there is a grade with no sections, you can set it that way.

```
8A
    monday  tuesday wednesday thursday   friday
1    Bible    Bible     Bible    Bible    Bible
2     Lang     Lang      Lang     Lang     Lang
3     Math     Math      Math     Math     Math
4  History  History   History  History  History
5  Science  Science   Science  Science  Science
6    Choir    Choir     Choir    Choir     ArtA
7      Gym  Chinese    StudyA  Chinese      Gym

8B
    monday  tuesday wednesday thursday   friday
1     Lang     Lang      Lang     Lang     Lang
2    Bible    Bible     Bible    Bible    Bible
3  History  History   History  History  History
4     Math     Math      Math     Math     Math
5     Band     Band      Band     Band   StudyB
6  Science  Science   Science  Science  Science
7      Gym  Spanish      ArtB  Spanish      Gym

7A
  monday tuesday wednesday thursday friday
1   None    None      None     None   None
2   None    None      None     None   None
3   None    None      None     None   None
4   None    None      None     None   None
5   None    None      None     None   None
6  Choir   Choir     Choir    Choir   None
7   None    None      None     None   None

7B
  monday tuesday wednesday thursday friday
1   None    None      None     None   None
2   None    None      None     None   None
3   None    None      None     None   None
4   None    None      None     None   None
5   Band    Band      Band     Band   None
6   None    None      None     None   None
7   None    None      None     None   None
