"""Replace faculty and admin avatar divs with profile dropdown wrappers - single line versions."""

with open("Academic_Resilience_Platform (1).html", "r", encoding="utf-8") as f:
    c = f.read()

# ── Faculty avatar (single line) ──
old_fac = '        <div class="tb-avatar" style="background:linear-gradient(135deg,#F59E0B,#FCD34D);color:#78350F;font-size:.73rem">Dr</div>'
new_fac = (
    '        <div class="profile-wrap">\n'
    '          <div class="tb-avatar" style="background:linear-gradient(135deg,#F59E0B,#FCD34D);color:#78350F;font-size:.73rem" id="facAvatarTop" onclick="toggleProfileDrop(\'facDrop\')">Dr</div>\n'
    '          <div class="profile-dropdown" id="facDrop">\n'
    '            <div class="pd-header"><div class="pd-name" id="facDropName">Faculty</div><div class="pd-email" id="facDropEmail"></div></div>\n'
    '            <div class="pd-item" onclick="closeProfileDrop()"><i class="fas fa-user-cog"></i>Account Settings</div>\n'
    '            <div class="pd-divider"></div>\n'
    '            <div class="pd-item" onclick="closeProfileDrop();switchAccount()"><i class="fas fa-exchange-alt"></i>Switch User</div>\n'
    '            <div class="pd-item danger" onclick="closeProfileDrop();logout()"><i class="fas fa-sign-out-alt"></i>Sign Out</div>\n'
    '          </div>\n'
    '        </div>'
)

# ── Admin avatar (single line) ──
old_adm = '        <div class="tb-avatar" style="background:linear-gradient(135deg,#10B981,#34D399);color:#064E3B;font-size:.73rem">AD</div>'
new_adm = (
    '        <div class="profile-wrap">\n'
    '          <div class="tb-avatar" style="background:linear-gradient(135deg,#10B981,#34D399);color:#064E3B;font-size:.73rem" id="admAvatarTop" onclick="toggleProfileDrop(\'admDrop\')">AD</div>\n'
    '          <div class="profile-dropdown" id="admDrop">\n'
    '            <div class="pd-header"><div class="pd-name" id="admDropName">Administrator</div><div class="pd-email" id="admDropEmail"></div></div>\n'
    '            <div class="pd-item" onclick="closeProfileDrop();switchAdminTab(\'settings\',null)"><i class="fas fa-user-cog"></i>Account Settings</div>\n'
    '            <div class="pd-divider"></div>\n'
    '            <div class="pd-item" onclick="closeProfileDrop();switchAccount()"><i class="fas fa-exchange-alt"></i>Switch User</div>\n'
    '            <div class="pd-item danger" onclick="closeProfileDrop();logout()"><i class="fas fa-sign-out-alt"></i>Sign Out</div>\n'
    '          </div>\n'
    '        </div>'
)

if old_fac in c:
    c = c.replace(old_fac, new_fac, 1)
    print("Faculty avatar replaced OK")
else:
    print("Faculty NOT found - searching nearby...")
    idx = c.find("FCD34D")
    while idx > 0:
        chunk = c[idx-150:idx+50]
        if "tb-avatar" in chunk:
            print("Found near:", repr(chunk))
            break
        idx = c.find("FCD34D", idx+1)

if old_adm in c:
    c = c.replace(old_adm, new_adm, 1)
    print("Admin avatar replaced OK")
else:
    print("Admin NOT found - searching nearby...")
    idx = c.find("34D399")
    while idx > 0:
        chunk = c[idx-150:idx+50]
        if "tb-avatar" in chunk:
            print("Found near:", repr(chunk))
            break
        idx = c.find("34D399", idx+1)

with open("Academic_Resilience_Platform (1).html", "w", encoding="utf-8") as f:
    f.write(c)
print("File saved.")
