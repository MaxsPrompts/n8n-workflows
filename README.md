Goal
Build a service that turns a plain language prompt into an n8n workflow file the user can import with one click.

Must Deliver
• A prompt box in a basic web page
• A server route that receives the text, calls an LLM, receives structured JSON, and sends it back to the page
• Client code that triggers the download of that JSON as workflow.json
• Validation that the JSON imports without errors in n8n

Inputs You Will Get
• Current HTML mockup
• Existing Python script that already converts text to a workflow object
• My OpenAI key or an environment variable where you can place yours

Success Criteria
• A user types “Watch Gmail for label X then forward to Notion”
• The page returns a file
• The file imports in n8n and runs without manual edits
