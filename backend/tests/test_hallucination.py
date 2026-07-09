from sentence_transformers import CrossEncoder
import numpy as np

ce = CrossEncoder('cross-encoder/nli-distilroberta-base')

# Test 1: Hallucination (contradiction)
context1 = "Project X is complete"
response1 = "Project X is still ongoing"
scores1 = ce.predict([[context1, response1]])
print(f"Test 1 (hallucination): {scores1[0]}")  # Should be high contradiction

# Test 2: Consistent
context2 = "Project X is complete"
response2 = "Project X has finished"
scores2 = ce.predict([[context2, response2]])
print(f"Test 2 (consistent): {scores2[0]}")  # Should be low contradiction

# Test 3: Consistent
context3 = """# GDG Dev Fest October Volunteering

**From**: sawzank@gmail.com (Shasanka Acharya)
**Date**: 2013-12-23T23:15:00
**Thread**: sawzank@gmail.com_20131223

---

Hi there!

Thank you for filling out the volunteering form for GDG DevFest.

We're excited to have you on board! 🎉

Please confirm your participation by replying to this email. Once confirmed, 
we'll reach out to you shortly with further details and next steps.

Looking forward to seeing you at the event!

Best regards,
Shasanka Acharya
GDG Sydney"""

response3 = """Based on the email excerpt, 
it appears that GDG Dev Fest is an event organized by Google Developers Group (GDG) Sydney. 
The exact details of the event are not specified in this email, 
but it seems to be a gathering or festival related to developer and technology-related topics, 
given the mention of volunteering and participation.
"""
scores3 = ce.predict([[context3, response3]])
print(f"Test 3 (consistent): {scores3[0]}")  # Should be low contradiction
