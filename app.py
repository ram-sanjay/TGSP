#!/usr/bin/env python3

import aws_cdk as cdk

from tgsp.tgsp_stack import TgspStack


app = cdk.App()
TgspStack(app, "TgspStack")

app.synth()
