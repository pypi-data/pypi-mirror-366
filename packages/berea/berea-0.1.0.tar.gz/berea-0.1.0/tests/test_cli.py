import pytest
import sys

from berea.cli import main, CLIConfig
from berea.utils import get_downloaded_translations


@pytest.mark.parametrize(
    "msg, args, output", 
    [
        (
            "Printing a single verse failed",
            ['john', '3', '16'],
            (
                "For God so loved the world that He gave His one and only Son, that everyone\n"
                "who believes in Him shall not perish but have eternal life. "
            )
        ),
        (
            "Printing multiple verses failed",
            ['john', '3', '16-18'],
            (
                "For God so loved the world that He gave His one and only Son, that everyone\n"
                "who believes in Him shall not perish but have eternal life. For God did not\n"
                "send His Son into the world to condemn the world, but to save the world\n"
                "through Him. Whoever believes in Him is not condemned, but whoever does not\n"
                "believe has already been condemned, because he has not believed in the name of\n"
                "God’s one and only Son. "
            )
        ),
        (
            "Printing multiple verses with verse numbers failed",
            ['john', '3', '16-18', '-n'],
            (
                "16 For God so loved the world that He gave His one and only Son, that everyone\n"
                "who believes in Him shall not perish but have eternal life. 17 For God did not\n"
                "send His Son into the world to condemn the world, but to save the world\n"
                "through Him. 18 Whoever believes in Him is not condemned, but whoever does not\n"
                "believe has already been condemned, because he has not believed in the name of\n"
                "God’s one and only Son. "
            )
        ),
        (
            "Printing a chapter failed",
            ['psa', '117'],
            (
                "Praise the LORD, all you nations! Extol Him, all you peoples! For great is His\n"
                "loving devotion toward us, and the faithfulness of the LORD endures forever.  \n"
                "Hallelujah! "
            )
        ),
        (
            "Printing a chapter with verse numbers failed",
            ['psa', '117', '-n'],
            (
                "1 Praise the LORD, all you nations! Extol Him, all you peoples! 2 For great is\n"
                "His loving devotion toward us, and the faithfulness of the LORD endures\n"
                "forever.   Hallelujah! "
            )
        ),
        (
            "Printing a book failed",
            ['3john'],
            (
                "The elder,  To the beloved Gaius, whom I love in the truth: Beloved, I pray\n"
                "that in every way you may prosper and enjoy good health, as your soul also\n"
                "prospers. For I was overjoyed when the brothers came and testified about your\n"
                "devotion to the truth, in which you continue to walk. I have no greater joy\n"
                "than to hear that my children are walking in the truth. Beloved, you are\n"
                "faithful in what you are doing for the brothers, and especially since they are\n"
                "strangers to you. They have testified to the church about your love. You will\n"
                "do well to send them on their way in a manner worthy of God. For they went out\n"
                "on behalf of the Name, accepting nothing from the Gentiles. Therefore we ought\n"
                "to support such men, so that we may be fellow workers for the truth. I have\n"
                "written to the church about this, but Diotrephes, who loves to be first, will\n"
                "not accept our instruction. So if I come, I will call attention to his\n"
                "malicious slander against us. And unsatisfied with that, he refuses to welcome\n"
                "the brothers and forbids those who want to do so, even putting them out of the\n"
                "church. Beloved, do not imitate what is evil, but what is good. The one who\n"
                "does good is of God; the one who does evil has not seen God. Demetrius has\n"
                "received a good testimony from everyone, and from the truth itself. We also\n"
                "testify for him, and you know that our testimony is true. I have many things\n"
                "to write to you, but I would prefer not to do so with pen and ink. Instead, I\n"
                "hope to see you soon and speak with you face to face.  Peace to you.  The\n"
                "friends here send you greetings.  Greet each of our friends there by name. "
            )
        ),
        (
            "Printing a book with verse numbers failed",
            ['3john', '-n'],
            (
                "1 The elder,  To the beloved Gaius, whom I love in the truth: 2 Beloved, I\n"
                "pray that in every way you may prosper and enjoy good health, as your soul\n"
                "also prospers. 3 For I was overjoyed when the brothers came and testified\n"
                "about your devotion to the truth, in which you continue to walk. 4 I have no\n"
                "greater joy than to hear that my children are walking in the truth. 5 Beloved,\n"
                "you are faithful in what you are doing for the brothers, and especially since\n"
                "they are strangers to you. 6 They have testified to the church about your\n"
                "love. You will do well to send them on their way in a manner worthy of God. 7\n"
                "For they went out on behalf of the Name, accepting nothing from the Gentiles.\n"
                "8 Therefore we ought to support such men, so that we may be fellow workers for\n"
                "the truth. 9 I have written to the church about this, but Diotrephes, who\n"
                "loves to be first, will not accept our instruction. 10 So if I come, I will\n"
                "call attention to his malicious slander against us. And unsatisfied with that,\n"
                "he refuses to welcome the brothers and forbids those who want to do so, even\n"
                "putting them out of the church. 11 Beloved, do not imitate what is evil, but\n"
                "what is good. The one who does good is of God; the one who does evil has not\n"
                "seen God. 12 Demetrius has received a good testimony from everyone, and from\n"
                "the truth itself. We also testify for him, and you know that our testimony is\n"
                "true. 13 I have many things to write to you, but I would prefer not to do so\n"
                "with pen and ink. 14 Instead, I hope to see you soon and speak with you face\n"
                "to face.  Peace to you.  The friends here send you greetings.  Greet each of\n"
                "our friends there by name. "
            )
        ),
        (
            "Printing a different translation failed",
            ['john', '3', '16', '-t', 'KJV'],
            (
                "For God so loved the world, that he gave his only begotten Son, that whosoever\n"
                "believeth in him should not perish, but have everlasting life. "
            )    
        ),
        (
            "Creating a Markdown excerpt failed",
            ['john', '3', '16', '-f', 'md'],
            (
                "###\n\n"
                "______________________________________________________________________\n\n"
                "For God so loved the world that He gave His one and only Son, that everyone\n"
                "who believes in Him shall not perish but have eternal life. \n"
                "([John 3:16 BSB](https://www.stepbible.org/?q=version=BSB@reference=john.3.16&options=NVHUG))\n\n"
                "______________________________________________________________________"
            )
        ),
        # The BSB contains empty verses for cross-references to verses present
        # in some manuscripts
        (
            "Skipping empty verses failed",
            ['mark', '9', '43-47', '-n'],
            (
                "43 If your hand causes you to sin, cut it off. It is better for you to enter\n"
                "life crippled than to have two hands and go into hell, into the unquenchable\n"
                "fire. 45 If your foot causes you to sin, cut it off. It is better for you to\n"
                "enter life lame than to have two feet and be thrown into hell. 47 And if your\n"
                "eye causes you to sin, pluck it out. It is better for you to enter the kingdom\n"
                "of God with one eye than to have two eyes and be thrown into hell, "
            )
        )
    ]
)
def test_reference(monkeypatch, capsys, msg, args, output):
    args.insert(0, 'bible')
    monkeypatch.setattr(sys, 'argv', args)
    
    main()
    
    captured = capsys.readouterr()
    assert captured.out == output + '\n', msg


def test_delete(monkeypatch):
    default_translation = CLIConfig.get_default_translation()
    monkeypatch.setattr(sys, 'argv', ['bible', 'delete', default_translation])
    main()
    
    assert not pytest.translation_exists(default_translation)
    
    downloaded_translations = get_downloaded_translations()
    
    msg = "Failed to update config after deleting default translation"
    new_default_translation = CLIConfig.get_default_translation()
    assert new_default_translation == downloaded_translations[0], msg
    
    # Delete remaining translations
    for translation in downloaded_translations:
        monkeypatch.setattr(sys, 'argv', ['bible', 'delete', translation])
        main()
    
        assert not pytest.translation_exists(translation)
    
    msg = "Failed to update config if no other translation is downloaded"
    assert CLIConfig.get_default_translation() == 'None', msg


def test_download_sets_default_translation(monkeypatch):
    # Delete remaining translations if any exist
    downloaded_translations = get_downloaded_translations()
    if downloaded_translations:
        for translation in downloaded_translations:
            monkeypatch.setattr(sys, 'argv', ['bible', 'delete', translation])
            main()
    
    monkeypatch.setattr(sys, 'argv', ['bible', 'download', 'BSB'])
    main()
    
    msg = "Failed to set first download as the default translation"
    assert CLIConfig.get_default_translation() == 'BSB', msg


@pytest.mark.parametrize(
    "translation",
    [
        ('KJV'),
        ('BSB'),
        ('LEB'),
        ('RLT'),        
        ('UKJV'),        
    ]
)
def test_download(monkeypatch, translation):
    if translation in get_downloaded_translations():
        monkeypatch.setattr(sys, 'argv', ['bible', 'delete', translation])
        main()
    
    args = ['bible', 'download']
    args.append(translation)
    monkeypatch.setattr(sys, 'argv', args)
    
    main()
    
    assert pytest.translation_exists(translation)


@pytest.mark.parametrize(
    "msg, args, output",
    [
        (
            "Searching a phrase with a single occurrence failed",
            ['rescue my soul', '-t', 'BSB'],
            (
                "1 occurrences of 'rescue my soul' in the BSB Bible:\n"
                "___\n\n"
                "Psalms 35:17:\n"
                "How long, O Lord, will You look on? Rescue my soul from their ravages, my precious life from these lions. \n"
                "___\n"
            )
        ),
        (
            "Searching a phrase with multiple occurrences failed",
            ['sheep gate', '-t', 'BSB'],
            (
                "4 occurrences of 'sheep gate' in the BSB Bible:\n"
                "___\n\n"
                "Nehemiah 3:1:\n"
                "At the Sheep Gate, Eliashib the high priest and his fellow priests began rebuilding. They dedicated it and installed its doors. After building as far as the Tower of the Hundred and the Tower of Hananel, they dedicated the wall. \n"
                "___\n\n"
                "Nehemiah 3:32:\n"
                "And between the upper room above the corner and the Sheep Gate, the goldsmiths and merchants made repairs. \n"
                "___\n\n"
                "Nehemiah 12:39:\n"
                "over the Gate of Ephraim, the Jeshanah Gate, the Fish Gate, the Tower of Hananel, and the Tower of the Hundred, as far as the Sheep Gate. And they stopped at the Gate of the Guard. \n"
                "___\n\n"
                "John 5:2:\n"
                "Now there is in Jerusalem near the Sheep Gate a pool with five covered colonnades, which in Hebrew is called Bethesda. \n"
                "___\n"
            )
        ),
        (
            "Searching a phrase in the Old Testament failed",
            ['holy spirit', '-OT', '-t', 'BSB'],
            (
                "3 occurrences of 'holy spirit' in the Old Testament (BSB):\n"
                "___\n\n"
                "Psalms 51:11:\n"
                "Cast me not away from Your presence; take not Your Holy Spirit from me. \n"
                "___\n\n"
                "Isaiah 63:10:\n"
                "But they rebelled and grieved His Holy Spirit. So He turned and became their enemy, and He Himself fought against them.   \n"
                "___\n\n"
                "Isaiah 63:11:\n"
                "Then His people remembered the days of old, the days of Moses. Where is He who brought them through the sea with the shepherds of His flock? Where is the One who set His Holy Spirit among them, \n"
                "___\n"
            )
        ),
        (
            "Searching a phrase in the New Testament failed",
            ['ghost', '-NT', '-t', 'BSB'],
            (
                "2 occurrences of 'ghost' in the New Testament (BSB):\n"
                "___\n\n"
                "Matthew 14:26:\n"
                "When the disciples saw Him walking on the sea, they were terrified. “It’s a ghost!” they said, and cried out in fear. \n"
                "___\n\n"
                "Mark 6:49:\n"
                "but when they saw Him walking on the sea, they cried out, thinking He was a ghost— \n"
                "___\n"
            )
        ),
        (
            "Searching a phrase in a book failed",
            ['lying spirit', '2chr', '-t', 'BSB'],
            (
                "2 occurrences of 'lying spirit' in II Chronicles (BSB):\n"
                "___\n\n"
                "II Chronicles 18:21:\n"
                "And he replied, ‘I will go out and be a lying spirit in the mouths of all his prophets.’  ‘You will surely entice him and prevail,’ said the LORD. ‘Go and do it.’ \n"
                "___\n\n"
                "II Chronicles 18:22:\n"
                "So you see, the LORD has put a lying spirit in the mouths of these prophets of yours, and the LORD has pronounced disaster against you.” \n"
                "___\n"
            )
        ),
        (
            "Searching a phrase in a chapter failed",
            ['lampstands', 'rev', '1', '-t', 'BSB'],
            (
                "3 occurrences of 'lampstands' in Revelation of John 1 (BSB):\n"
                "___\n\n"
                "Revelation of John 1:12:\n"
                "Then I turned to see the voice that was speaking with me. And having turned, I saw seven golden lampstands, \n"
                "___\n\n"
                "Revelation of John 1:13:\n"
                "and among the lampstands was One like the Son of Man, dressed in a long robe, with a golden sash around His chest. \n"
                "___\n\n"
                "Revelation of John 1:20:\n"
                "This is the mystery of the seven stars you saw in My right hand and of the seven golden lampstands: The seven stars are the angels of the seven churches, and the seven lampstands are the seven churches. \n"
                "___\n"
            )
        ),
        (
            "Searching a phrase in a passage with the New Testament flag should be invalid",
            ['lampstands', 'rev', '1', '-NT'],
            (
                "Invalid search: cannot search a passage with the '-NT, --new_testament' flag."
            )
        ),
        (
            "Searching a phrase in a passage with the Old Testament flag should be invalid",
            ['holy spirit', 'isa', '-OT'],
            (
                "Invalid search: cannot search a passage with the '-OT, --old_testament' flag."
            )
        ),
    ]
)
def test_search(monkeypatch, capsys, msg, args, output):
    args = ['bible', 'search'] +  args
    monkeypatch.setattr(sys, 'argv', args)
    
    main()
    
    captured = capsys.readouterr()
    assert captured.out == output + '\n', msg


@pytest.mark.parametrize(
    "translation",
    [
        ('KJV'),
        ('LEB'),
        ('RLT'),        
        ('UKJV'),      
        ('BSB'), 
    ]
)
def test_config_default_translation(monkeypatch, translation):
    args = ['bible', 'config', 'translation', translation]
    monkeypatch.setattr(sys, 'argv', args)
    
    main()
    
    msg = "Setting the default translation failed"
    assert CLIConfig.get_default_translation() == translation, msg
