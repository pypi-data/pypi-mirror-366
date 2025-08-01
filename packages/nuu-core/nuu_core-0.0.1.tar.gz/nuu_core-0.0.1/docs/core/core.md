## Building an AI-First Organization from the Ground Up

### The Minimum Viable Solution for Knowledge Management

We want NUU Cognition to be an AI organization from the ground up. The things we choose and the way we engage and work on it should reflect that. It's much easier to start from scratch than it is to integrate into an existing system.

So, we need ways to store meeting context. The thing is, we want to do this as quickly as possible with the minimum overhead possible because we want to dedicate most of our time to building the actual products and winning the competition. We need a minimum viable solution to the AI org part of NUU Cognition. We have very limited resources on what we can do, and we need to still be able to capture everything and have some sort of way to do it.

I don't think it's even worth setting up a database and things like that. We can almost do a lot of things manually, like manually pasting meeting context.

### The "Contexter" Tool and Markdown-Based System

We could take inspiration from the method I was looking at where one markdown file references other markdown files. Then we can create a program for the parsing, and that is not that hard. I'm actually working on it right now; it's called Contexter. With Contexter right now, you can watch files and folders. So if you watch the source folder, then you do `contexter sync`, it will copy all the files in the source and put it into one copy-pastable thing. We can easily extend this so that if you have a markdown file, it will fetch all the referenced markdowns and then compile it. I can do that in the background, so we can have access to that tool.

What it would look like is, we could probably have an Obsidian vault or a GitHub repository of markdown files. Imagine this is a project, and in that project, we have to find a syntax to be able to reference other markdown files. Basically, we link, for example, meeting one and meeting two, and then we run it through Contexter, and it will generate the full context for meeting two. Then we can just copy this directly to the AI.

That's what Obsidian does, kind of. But Obsidian doesn't have this compiled feature. It does actually have a compile feature where you use the double brackets. We'd have to use Obsidian to generate this. We would want our own, and that would be best, I think. But at the end of the day, because we're limiting our resources, it might be sufficient to just do it manually. It's not that bad. It's not impossibly hard.

### Demonstrating the Personal Knowledge System (Obsidian)

So then we kind of need to organize the structure of each thing. One thing is that we need to remove folders. This concept of folders needs to be removed because the great thing about Obsidian is when you try to hyperlink, it searches for you, so you don't need a folder system. You can just dump all markdown into this big folder, and every single markdown file is in that folder. But then you're able to index on top of it. You don't need to look at folders; you just look at the names. The names themselves are the way we interact with the information.

But when it gets too big, how is that?

I don't think it will because we're just doing string matching, so it shouldn't ever really get too big. I'll show you what that looks like on my computer, in my vault. I don't have folders. Well, I do have folders, but they're not for markdown; they're for other files.

Alright, this is a note I'm working on. The vault is where I have all my markdown files. See, every file is in here. These are all files. Everything else is not actual files. This is a file, but this is just for daily notes. And these are more like raw stuff.

The vision for me is that we each have our own cognition operating system, right? It should have access to all of the chats that you've had with all your different AIs. It should be that every piece of information or knowledge that you have should be accessible in this central software. Obsidian is currently our best implementation of that because I can put anything in Obsidian. This is a ChatGPT chat I can put in here. If there are videos, I can put them in here. The rest of this is really more like raw sources. If I have books, I do have books, but I haven't moved them. I'm thinking about courses and academic papers; they go in here. And this is for image files and things like that, so all my Excalidraw files are in here.

### The Power of a Folderless, Linked System

If you think about what this is, this is my personal knowledge system. My personal memory. And you see how 99% of it is in markdown. And again, all of it's in this one vault. If I want to access something, I just do control-O and I find it. So if I have a bunch of philosophy on learning, I just type "philosophy of learning," and then it goes here. You can see this is kind of like the folder. The actual file itself is the folder because here it would contain links to the next thing. Everything is linked. You're not trying to find it in the file list; you're just finding it through the search. It makes sense.

This is an example of exporting. This is the raw markdown view, but inside Obsidian, if you use an exclamation mark, it will render it as an embedding. As you can see, I've embedded all my learning writing, and now it's like this. We can actually export it, and it will export this. That's what I was talking about. You can see this is a manual process, but it's not bad. Even if it's a manual process, it's fine. But I'm pretty sure we can indeed create our own rendering compiler.

The problem with this is that there are no folders. If we had folders, then the program would have to match this title inside all subfolders to see if there's a duplicate, and if there's a duplicate, it might get a bit complicated.

Can you have duplicates now?

Yeah, you can have duplicates. I think they name it slightly differently. So if I try, and then we go back... alright, here, let's do this. Okay, so then it will link to this one. And this is a great thing about Obsidian: you can nickname the link. It's nicknamed with that symbol. It's really easy to work with text inside Obsidian.

## Refining the Internal Workflow

### A Simplified Prompt System for the Competition

I think we can have all our knowledge inside of Obsidian, and we can set up that Git thing again for NUU Cognition. This is almost like a version of that prompt program. What that prompt program does is it kind of compiles a bunch of files, but the extra thing the prompt program has is checklists. A checklist is a sequence of things that needs to be done for a task, perhaps. I think you can invoke the checklist, and it will go through a bunch of steps to see if it meets the criteria. I don't think that's too necessary for what we're doing, but they do have tasks, and tasks are quite cool because they have these instructions to do a task. This is the instruction to create a documentation thing, and it basically dynamically loads the tasks. So if you wanted to do a task, it would then fetch that file and then do the task. It won't load all the tasks to the context first; only if you trigger it will it do it.

So we're basically building the prompt application for NUU Cognition?

Yes, instead of doing what we're doing here, which takes more time. Technically, what we're doing here is better because it's able to more dynamically do stuff and has a higher ceiling, but we don't have time to do it. So we'll do a prompt system in this instead, and that should follow the 80/20 rule of least effort, most return. I think that's a good way to start, and then we can transition eventually. Hopefully.

It makes sense, too. This is just for the competition. The time frame is not long. For the competition right now, we use this system. And again, we first have to prove that it works. We're still researching whether the AI@DSCubed thing can actually work because we have all these theories of integrating everything and retrieval systems, but we haven't built it yet, so we don't even know if it works. But this is 100% guaranteed to work. We're basically hand-picking the context. And later, we can make another layer where it can transition. Exactly.

### Clarifying the Role of AI in NUU Cognition's Products

Another big difference is we're not going to let AI take too many actions. We're not going to give it too many tools. Things like creating tasks, we can just do it now. Because we are a small team, actually doing tools is a bit less involved. For example, instead of automating the emails, it can just draft the emails, and then we can take it that extra step. So for us, it's less like a full AI organization but like an AI-assisted knowledge base.

What parts of NUU are going to be using AI? Like the actual applications?

Well, it depends on the particular tool. For NUU Surf, obviously in summarizing. It's just to summarize. That doesn't even require a framework because it's just API calls. Branching will use AI as the main interface. Branching is the one where you can have AI conversations and then you can highlight a word and branch out of the conversation. For that one, obviously, the conversation is AI, and you can choose the model and things like that. It depends. What do we call that? NUU Expand? The suggestion you have, you expand? NUU Brainstorm, NUU Inspire. NUU Reason. It helps you reason, helps with critical thinking.

But AI is less important than the actual... it's not as important. We are not an AI-first company. We're a software-first company. It's more about the UI and the code and a little bit about the AI. The AI is very deterministic. We don't want an AI agent. I want to make sure it's very deterministic and reliable.

### The Internal "AI-Assisted Knowledge Base"

Which part are we going to use the prompting thing for?

This is for internal stuff. This is for if we're planning a project, it helps out with suggestions. If we're trying to win the competition, it helps us win the competition. This is the AI org. What do we call this system?

If you think about what we're doing, we're writing software to interact with information. And that can be done individually or as an organization. So this is kind of the collaborative side of NUU Cognition because you're all collaborating on these documents behind the scenes. This system we're building now, like a prompt system, this can have a name as well. And we can sell that as a product. There are so many things that could be done here.

But we have this prompt system. For example, after this meeting is done, we'll convert it into markdown, and then we'll chuck it in the vault and create a new note that is for this project. Then we link it to that note. Now, in the future, if we want to work on this part, we just load up that note and write notes and information in there for the future. The meetings are in there, and then we can just export that whole thing into ChatGPT or Claude, get it to help us brainstorm or do stuff like that.

For me, the best thing is, because I have Claude 3 Opus Pro, which is by far the smartest one in the world, but you cannot use it through the API. It's like $100, really, really expensive. So we need to get the content and paste it through the web UI.

Here we can also have our knowledge on the strategy side, like the strategy of how we're planning to brand or market. All of that. And eventually, we'll just have everything at this base, all markdown, all knowledge. A true knowledge management system. All knowledge of the organization should be here, and that's how we can put it all into context. So instead of building an automated retrieval system, we're manually doing the retrieval part. And then we're just putting it into AI to get us to create branding, create copywriting, create the site, find the requirements, and things like that. That would be the easiest solution. We don't have to write any database code, don't need to have any tools. I think we can set that up, and then we'll see how that goes.

## Competition Strategy and Logistics

### Team Availability and Workload

So how busy are you over the next week? Or the next two months?

I was taking one course that is quite heavy, and then one I decided to take an easy subject. But then I had that meeting with the PhD last time, and he said, "Can you change that subject to some other AI-related subject?" So it increased my workload. Now there are basically all four that are pretty hard.

So you're doing that. How many hours do you study a week? You have to make sure you get H1s.

It should be fine because the competition is not us doing the whole thing. And it's at the end of September, so it is fine. I can start the work after the competition for the heavy work. I think that's where all the big assignments are going to come out. But we're going to win, and then this is going to be a company. Then school doesn't really matter now if you win this.

How about we go all in for the first month? See how far we can go? So how many hours do you work? We can take a step back from the AI@DSCubed in the sense that most of this stuff is AI-generated anyway. I can work on that in the background.

### The Challenge of Pitching a Grand Vision

The preliminary round is a video, actually. We really need to see what they're looking for because I feel like it's hard to pitch what we have because it's not just one point. We can't validate it. We have to focus. Either we're advertising this one product or NUU Cognition. You can't do both.

That's the thing. It's a very unique situation in that we have a vision, and the vision is very clear, I feel. People will understand this: tools to help you think better. And then we can link some research and things like that, like the intersection between software and cognitive psychology. Then we can demonstrate that through a couple of examples. That's the idea.

The market would be everyone. But obviously, we have to be a bit more specific. Learners. People who are learning. Learners, knowledge workers, researchers. So we're pitching to investors, right? I think so. Not the general public, so they should have some knowledge. Because this "cognitive" word is pretty heavy for the general public. It's like, you're kind of dumb. "Think," though. "Think" is easy. "Help us think better." But they'll be like, "Oh, I know how to think." It's like, "Let's help normal people think." "I know how to think." "I have to help you remember more stuff."

I think it's almost like each app will have its own target audience. For heavy readers, NUU Surf would be the one.

### Go-to-Market Ideas for Student Users

We should actually have a really good one for interacting with audio and podcasts. Because when you listen to a podcast, you forget it because there's no way to see the information again. Once the audio is played, it's hard to jump back. I'd say you listen to the audio and it's like, "Oh, that's pretty cool," and then you're never going to find it again because the video is like three hours long, or a podcast is like two hours.

I've seen something that generates in real-time.

No, what it does is it generates checkpoints within your audio. So you have a visual way to jump back to places within the audio. Otherwise, you have no idea what time they spoke about what. Just like NUU Surf helps us interact with text information, this app would help us interact with audio information. It's all about the interaction.

So it's like every application has its own target audience. Once they get on the app, then they can discover more of the ecosystem. And then the ecosystem is all of this, but also the central members.

### The Bigger Picture: Creating a New Field of Study

Because this field itself, this is a field of secondary software and thinking. This is a new field that we haven't even begun as a species to look into. So we're almost like putting a name on the field, and then we're trying to make money out of the field. We're creating this field not as an academic pursuit, but as a practical pursuit. And because it's practical, we get the most amount of feedback and the most amount of data to do the research. Because we're researching the UI/UX of how we interact with information.

So it's everything. It's this field. And this field is not only the software, not only the people who use it, but it's this whole thing. And it's done through these little things. This field touches everyone's lives; everyone's interacting with information, and everyone's learning every day. So we need a way to pitch that, and that's the hardest part. It's going too big, really. It's too big.

So we need to pitch these apps. Either we lead with the grand vision and say, "Okay, hang on a minute. We know this is really big. We'll pin it down," or we just go first with the applications and then say that these applications build up to a vision of the future.

I think the second one is better.

Okay. So let's say the pitch is five minutes. Maybe we spend like four minutes on that, and the last minute you can go over your higher vision.

No, because I think they want a lot of market research and stuff like that. So we'll have to look into it.

## Finalizing the Plan

### Tailoring the Pitch to the Judges

That stuff can be... we can fake that. I mean, not fake, but we can generate some slides. We can fake some data. It's okay. That's where AI comes in, which is good. AI can help us with market research, for sure. We need to talk to customers.

This is why I think if we made a quick lecture summary tool, specifically for university students, and we advertise it somewhere, when we tell people, I think that will help get the word out. A lecture summary is almost the gateway into this. Lecture summaries help you understand the lecture. It's the entry point. And if we show that a simple app like this is so rudimentary and people are interested in it, then where does everything else fit? A lecture tool would be useful to me. It would be useful to everyone. So we'd really focus on being useful.

I don't know if they'll get it, though. This is not a normal startup. A normal startup is one product. It's just one thing. So we do have to really talk to the judges and ask. I think they do have a workshop session. They have a lot. So we need to get there and ask them. I think to win the competition is not even about the idea itself, it's about cheating the judges. We need to get loud. And then after we win, then we can form a full company.

### Next Steps and Immediate Actions

So are we all officially starting next Monday?

Yeah, we're officially starting today. Might as well. We'll get that done as soon as possible. I think I'll get that done today. It's pretty fast. It's literally just a structure. We've got to discuss what tools, and the actual timeline. Yes, I think we do really need to see the judging criteria.

One potential way is we advertise to clubs, to the psychology club, and say something like, "We're starting a research community," or some language to make it up. And then people who are interested in that can sign up with their email or something. Tell them about study tips. Again, we're kind of in study tips as well. So we can collaborate with them. There's just so much to do in this space, so much value to be generated with the simplest of things.

It's very general, like learning. So researchers... we have to pitch to the people. Because it's such a general idea, the pitch is so different for each person. For investors, it's about who's interested in this, do we have proof of it, and the money. It's about the money and the business model. For students, it's about helping them to study. For thinkers, it's about how it helps you think. For corporate people, how much time it saves.

### The Ethics of "Faking It" for a Pitch

I think a figure would be really nice, like a statistic on how much percent it increases industrial efficiency. It's very straightforward.

We can fake that. Of course. I can fake the sign-ups as well.

Yeah, it's okay. No one cares. No one's going to look. It's an anonymous submission anyway.

We should check the criteria. I don't think there is a criteria.
