Roadmap: this is the rough roadmap for this project.

1. Basic fact-based knowledge base flow
    a. Hardcoded
        i. ~~Hardcode inputs (Slack messages)~~
        ii. ~~Hardcode knowledge base guidelines~~
        iii. ~~Hardcode fact-based knowledge base~~
        iv. ~~Send Slack messages, knowledge base guidelines, and fact-based
        knowledge base to the ChatGPT API to update fact-based knowledge
        base (log what's sent)~~
        v. ~~Receive the new fact-based knowledge base from ChatGPT API (log
        what's received)~~
        vi. ~~Deploy to Vercel and test flow~~
    b. Full
        i. ~Read Slack messages (inputs) from Slack via Zapier (then deploy +
        test)~
        ii. Read knowledge base guidelines from a Google Doc (then deploy +
        test)
        iii. Read fact-based knowledge base from Google Sheets (then deploy +
        test) 
        iv. [existing ChatGPT API flow]
        v. Rep  lace data in previous fact-based knowledge base with new fact-
        based knowledge base (then deploy + test)
2. Agentic knowledge management
    a. Task generation
        i. Read knowledge management tasks from Supabase
        ii. Send fact-based knowledge base, knowledge base guidelines, and
        knowledge management tasks to ChatGPT API to generate tasks
        iii. Receive the new knowledge management tasks from ChatGPT API
        iv. Add new knowledge management tasks to the knowledge
        management tasks on Supabase
        v. Deploy to Vercel and test flow
    b. Task execution
        i. Independent
            1. Read independently executable tasks from knowledge
            management tasks on Supabase
            2. Send fact-based knowledge base, knowledge base guidelines, and
            knowledge management tasks to ChatGPT API to execute tasks
            3. [existing fact-based knowledge base updating flow]
            4. Remove completed knowledge management tasks
        ii. Slack-based [note: this section will require some refinement before
        execution]
            1. Read tasks requiring human input from knowledge management
            tasks on Supabase
            2. Send questions in #proj-rn-fbkb via Zapier
            3. Receive answers in thread via Zapier
            4. Send fact-based knowledge base, knowledge base guidelines,
            knowledge management tasks, and answers to ChatGPT API to
            update fact-based knowledge base
            5. [existing fact-based knowledge base updating flow]
            6. Remove completed knowledge management tasks