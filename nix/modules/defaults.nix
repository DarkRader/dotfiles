{ ... }:
{
  system.defaults = {
    NSGlobalDomain = {
      AppleInterfaceStyle = "Dark";
      # Finder sidebar icon size:
      # 1 = small, 2 = medium, 3 = large
      NSTableViewDefaultSizeMode = 2;
    };

    dock = {
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
    };
  };
}
