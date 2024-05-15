# AI Crew for screenwriting
## Introduction
Example script to automatically write a screenplay from a newsgroup post using agents with [Crew.ai] (https://github.com/joaomdmoura/crewAI) .
CrewAI orchestrates autonomous AI agents, enabling them to collaborate and execute complex tasks efficiently.
You can also try it out with a personal email with many replies back and forth and see it turn into a movie script.
Demonstrates:
- multiple API endpoints (offical Mistral, Together.ai, Anyscale)
- running single tasks: spam detection and scoring
- running a crew to create a screenplay from a newsgroup post by first analyzing the text, creating a dialogue and ultimately formatting it

By [Toon Beerten](toon@neontreebot.be)

## Example output

Input:

```
From: keith@cco.caltech.edu (Keith Allan Schneider)
Subject: Re: <Political Atheists?
Organization: California Institute of Technology, Pasadena
Lines: 50
NNTP-Posting-Host: punisher.caltech.edu

bobbe@vice.ICO.TEK.COM (Robert Beauchaine) writes:

>>I think that about 70% (or so) people approve of the
>>death penalty, even realizing all of its shortcomings.  Doesn't this make
>>it reasonable?  Or are *you* the sole judge of reasonability?
>Aside from revenge, what merits do you find in capital punishment?

Are we talking about me, or the majority of the people that support it?
Anyway, I think that "revenge" or "fairness" is why most people are in
favor of the punishment.  If a murderer is going to be punished, people
that think that he should "get what he deserves."  Most people wouldn't
think it would be fair for the murderer to live, while his victim died.

>Revenge?  Petty and pathetic.

Perhaps you think that it is petty and pathetic, but your views are in the
minority.

>We have a local televised hot topic talk show that very recently
>did a segment on capital punishment.  Each and every advocate of
>the use of this portion of our system of "jurisprudence" cited the
>main reason for supporting it:  "That bastard deserved it".  True
>human compassion, forgiveness, and sympathy.

Where are we required to have compassion, forgiveness, and sympathy?  If
someone wrongs me, I will take great lengths to make sure that his advantage
is removed, or a similar situation is forced upon him.  If someone kills
another, then we can apply the golden rule and kill this person in turn.
Is not our entire moral system based on such a concept?

Or, are you stating that human life is sacred, somehow, and that it should
never be violated?  This would sound like some sort of religious view.
 
>>I mean, how reasonable is imprisonment, really, when you think about it?
>>Sure, the person could be released if found innocent, but you still
>>can't undo the imiprisonment that was served.  Perhaps we shouldn't
>>imprision people if we could watch them closely instead.  The cost would
>>probably be similar, especially if we just implanted some sort of
>>electronic device.
>Would you rather be alive in prison or dead in the chair?  

Once a criminal has committed a murder, his desires are irrelevant.

And, you still have not answered my question.  If you are concerned about
the death penalty due to the possibility of the execution of an innocent,
then why isn't this same concern shared with imprisonment.  Shouldn't we,
by your logic, administer as minimum as punishment as possible, to avoid
violating the liberty or happiness of an innocent person?

keith
```

End result:

```
## Keith:
 Robert, I don't understand. You're opposed to the death penalty because of some misplaced sense of compassion for criminals?

## Robert:
 No, Keith. It's about fairness and justice. We can't just take a life because someone has taken another.

## Keith:
But what about the families of the victims? Don't they deserve justice?

## Robert:
Of course they do, but the death penalty doesn't bring them back. It just perpetuates a cycle of violence.

## Keith:
 I don't see it that way. If someone takes an innocent life, then their own life should be forfeit. It's only fair.

## Robert:
 But what if we make a mistake? What if we execute an innocent person?

## Keith:
 That's a rare occurrence. And besides, we have a justice system in place to prevent that.

## Robert:
 And what if that system fails? What then, Keith?

## Keith:
 Well, we have to trust that it won't.

## Robert:
 And what about the cost-effectiveness of imprisonment versus the death penalty?

## Keith:
 That's a valid point, but the cost shouldn't be the only factor we consider.

## Robert:
 Agreed. But what about the potential violation of an innocent person's liberty or happiness by keeping a guilty one in prison for life?

## Keith:
 That's a complex issue. But I believe that the state has a responsibility to protect its citizens, even if it means depriving an individual of their freedom.

## Robert:
 And what about the possibility of using electronic surveillance devices to monitor prisoners and ensure their rehabilitation?

## Keith:
 I'll leave that to the experts. But I still believe in the death penalty as a means of justice and fairness.

## Robert:
 I respect your opinion, Keith. But I'll continue to advocate for a more compassionate and reasonable approach.
```

## Running the Script
Can be run in a new python env and installing crewai

## Possible (non-local) endpoints
Easily select in the script which API endpoint to use:
- Official Mistral: benefit of having access to mistral-medium
- Together.ai: lots of models to choose from
- Anyscale: cheapest at the time of writing

## Disclaimer
This is provided as is. The motivation is that i learn best from actual samples and i hope you do too. Please understand i can't give support on this.

## License
MIT License.
