# How to Collect Your 11 Documents

Goal: 11 plain text files in this folder, each holding real student reviews/threads about
Georgia Tech CS courses and professors. Should take about 30 minutes. Just copy and paste.

## The rule for every file
At the very top of each `.txt` file, paste the URL you got it from on the first line, like this:

```
SOURCE: https://www.ratemyprofessors.com/professor/123456

[paste the reviews here]
```

That URL line is how your system will cite its sources later, so don't skip it.

## Where to get each one

### Files 1, 2, 3, 4, 10 — Rate My Professors (5 professors)
1. Go to https://www.ratemyprofessors.com and search "Georgia Institute of Technology".
2. Pick 5 different Computer Science professors. Try to get a mix: some highly rated, some low rated.
   (Disagreement between sources is good. It gives you a real failure case to write about later.)
3. On each professor's page, click "Load More Ratings" until all reviews show.
4. Select all the review text + the ratings, copy it, and paste into the matching file
   (`01_rmp_profA.txt`, `02_rmp_profB.txt`, etc.). Put the page URL on the top line.

### Files 5, 6, 7, 8, 11 — r/gatech threads (5 Reddit threads)
1. Go to https://www.reddit.com/r/gatech and use the search bar inside it.
2. Search things like: `CS professor`, `CS 1331`, `CS 1332`, `which professor`, `CS workload`.
3. Open 5 different threads that have lots of comments. Good ones to look for:
   - a "best/worst CS profs" thread
   - a "how hard is CS 1331 / 1332" thread
   - a thread about one specific course
   - a "which professor should I take" thread
   - a thread about CS workload / what to expect
4. Copy the original post AND the top comments into the matching file. Put the thread URL on the top line.

### File 9 — Course Critique (grade data)
1. Go to https://critique.gatech.edu
2. Look up 2 CS courses (for example CS 1331 and CS 1332).
3. Copy the average GPA and grade breakdown info into `09_coursecritique.txt` with the URL on top.

## When you're done
- You should have 11 `.txt` files in this folder, each starting with a SOURCE line.
- Open a few and skim them. Notice they are mostly short opinions, not long essays. That fact
  decides your chunking strategy in Milestone 2 (short text means smaller chunks).
- Then come back and we'll build the pipeline.
