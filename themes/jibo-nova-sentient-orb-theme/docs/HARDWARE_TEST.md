# Hardware acceptance record: NOVA Sentient Orb v1.0.2

Target: real Jibo running 5x1/OpenJibo and BEacon compatible with jibo-tbd >= 3.1.6.
Do not modify the working robot's firmware, TLS configuration, NOVA adapter or native skill packages.

Tester: __________________  Date: ________________  BEacon version: __________
Robot build: ______________  Release asset SHA256: ____________________________

- [ ] Backup/record the currently installed and active eye theme.
- [ ] Upload the **exact** `jibo-nova-sentient-orb-theme.zip` and verify the correct theme name/version.
- [ ] Confirm upload does NOT activate until Apply (if replacing an active theme, previous appearance remains until Apply).
- [ ] Apply. Verify centering, eye scale, and no visible square borders or clipped glow.
- [ ] Observe normal gaze motion across extremes and blinking; watch for texture artifacts.
- [ ] Check eyeClosed/petting/sleep blending; no distracting flash or unexpected image changes.
- [ ] Test Hey Jibo/listening and listening-to-idle transition; confirm the distinct blue illuminated iris activates only when listening.
- [ ] Test Talk to NOVA listening, processing, thinking, and speaking phases; record a photo of the blue listening iris and verify it does not stay lit while speaking.
- [ ] Check standard BEacon menus, Agent Mode and Talk to NOVA launch and exit behavior.
- [ ] Switch to None and verify stock appearance, then return to the theme.
- [ ] Restart Jibo/BEam normally; verify theme persistence and normal behavior.
- [ ] Test offline/reconnect and alternate theme switching if relevant.
- [ ] No robot crashes, stuck screen, speech regression or excessive clipping observed.

**Result:** [ ] PASS  [ ] FAIL  [ ] NOT RUN
**Notes / evidence:** ______________________________________________________

Do not certify production-ready until PASS is recorded for this actual build.
