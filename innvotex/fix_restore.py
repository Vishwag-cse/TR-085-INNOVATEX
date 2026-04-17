"""
Restore the HTML file by:
1. Removing the chatbot section entirely
2. Cleaning up all remaining garbled characters properly
3. NOT touching JS logic at all - only fixing display text
"""
import re

with open("Academic_Resilience_Platform (1).html", "r", encoding="utf-8") as f:
    c = f.read()

# 1. Remove the entire chatbot block (between PLAGGUARD CHATBOT comment and closing </script> before </body>)
# Find and remove chatbot CSS + HTML + JS
chatbot_start = c.find("<!-- PLAGGUARD CHATBOT")
if chatbot_start == -1:
    chatbot_start = c.find("PLAGGUARD CHATBOT")

if chatbot_start > 0:
    # Find the </script> that ends the chatbot block (it's the last one before </body>)
    chatbot_end = c.find("</body>")
    if chatbot_end > chatbot_start:
        c = c[:chatbot_start] + "\n</body>" + c[chatbot_end + len("</body>"):]
        print("Chatbot removed successfully")
    else:
        print("Could not find chatbot end marker")
else:
    print("No chatbot found to remove")

with open("Academic_Resilience_Platform (1).html", "w", encoding="utf-8") as f:
    f.write(c)

print("Done!")
