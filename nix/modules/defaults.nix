{ ... }:
{
  # Power / Energy management (Lock Screen -> Turn display off...)
  power.sleep = {
    # display = "never";
    display = 2;   # macOS default on battery (minutes)
    # display = 10;  # macOS default on power adapter (minutes)
  };

  system.defaults = {
    NSGlobalDomain = {
      AppleInterfaceStyle = "Dark";
      # Finder sidebar icon size:
      # 1 = small, 2 = medium, 3 = large
      NSTableViewDefaultSizeMode = 2;
    };

    dock = {
      largesize = 80;
      magnification = true;
      mineffect = "scale";
      minimize-to-application = true;
      autohide = true;
      show-recents = false;
    };

    finder = {
      FXPreferredViewStyle = "clmv";
      _FXSortFoldersFirst = true;
      NewWindowTarget = "Home";
      AppleShowAllExtensions = true;
    };

    trackpad = {
      Clicking = true;
      TrackpadRightClick = true;
    };

    # Lock Screen & Screen Saver settings
    screensaver = {
      # Require password after display turns off or screen saver begins
      askForPassword = true;
      askForPasswordDelay = 0;
    };

    # Lock Screen & Login Window behavior
    loginwindow = {
      # Show username and photo on lock screen
      HideUserAvatarAndName = false;

      # Show message when locked (custom banner text on lock screen)
      LoginwindowText = null;

      # When switching user, login window shows:
      # false = List of users, true = Name and password fields
      SHOWFULLNAME = false;

      # Show the Sleep, Restart and Shut Down buttons
      ShutDownDisabled = false;
      RestartDisabled = false;
      SleepDisabled = false;

      # Allow users to login as guests
      GuestEnabled = false;
    };

    CustomUserPreferences = {
      "com.apple.assistant.support" = {
        "Assistant Enabled" = false;
      };
      "com.apple.assistant.backedup" = {
        "Assistant Enabled" = false;
      };
      "com.apple.Siri" = {
        "StatusMenuVisible" = false;
        "UserHasDeclinedEnable" = true;
      };
      "com.apple.loginwindow" = {
        RetriesUntilHint = 0;
      };
    };
  };
}
