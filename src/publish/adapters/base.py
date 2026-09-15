"""Adapter contract. Real adapters are community plug-ins (one file per platform)."""
class Adapter:
    platform = "base"
    def prepare(self, row): raise NotImplementedError  # fill the form, return screenshot path; never click submit
    def submit(self, row): raise NotImplementedError   # click submit ONLY if row["confirmed"] is True; return post url
    def verify(self, url): raise NotImplementedError   # open url, True if the post is live
