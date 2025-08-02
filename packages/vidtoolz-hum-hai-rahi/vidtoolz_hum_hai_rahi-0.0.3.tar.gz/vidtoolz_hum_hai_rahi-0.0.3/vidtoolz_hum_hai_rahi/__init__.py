import vidtoolz
import os
import vidtoolz_apply_greenscreen as gs
import vidtoolz_add_sound.add_sound as snd


ASSETS = os.path.join(os.path.dirname(__file__), "assets")


def determine_output_path(input_file, output_file):
    input_dir, input_filename = os.path.split(input_file)
    name, _ = os.path.splitext(input_filename)

    if output_file:
        output_dir, output_filename = os.path.split(output_file)
        if not output_dir:  # If no directory is specified, use input file's directory
            return os.path.join(input_dir, output_filename)
        return output_file
    else:
        return os.path.join(input_dir, f"{name}_h2r.mp4")


def create_parser(subparser):
    parser = subparser.add_parser("h2r", description="Tools for hum hai rahi channel")
    # Add subprser arguments here.
    parser.add_argument("input", type=str, help="Input video to add the file.")
    parser.add_argument(
        "-o", "--output", type=str, default=None, help="Output file name"
    )
    parser.add_argument(
        "-i",
        "--intro",
        action="store_true",
        help="Adds Hum Hai Rahi intro video greenscreen (9s)",
    )
    parser.add_argument(
        "-sv",
        "--subscribe-voice",
        action="store_true",
        help="Adds subscribe greenscreen with voice (6s)",
    )
    parser.add_argument(
        "-s",
        "--subscribe",
        action="store_true",
        help="Adds subscribe greenscreen with no voice (5s)",
    )
    parser.add_argument(
        "-c",
        "--consider",
        action="store_true",
        help="Adds consider subscribing voice over (5s)",
    )
    parser.add_argument(
        "-a", "--apna-desh", action="store_true", help="Adds apna desh voice over (13s)"
    )
    parser.add_argument(
        "-l", "--like", action="store_true", help="Adds like-comment voice over (5s)"
    )
    parser.add_argument(
        "-w",
        "--watching",
        action="store_true",
        help="Adds you are watching voice over (6s)",
    )
    parser.add_argument(
        "-p",
        "--part-of-series",
        action="store_true",
        help="Adds you are Part of a series voice over (6s)",
    )

    parser.add_argument(
        "-stay",
        "--stay-tuned",
        action="store_true",
        help="Adds you are Stay Tuned and thanks for watching voice (3s) over",
    )
    parser.add_argument(
        "-st",
        "--start-time",
        type=float,
        default=1.0,
        help="Start time if given default=1",
    )

    return parser


class ViztoolzPlugin:
    """Tools for hum hai rahi channel"""

    __name__ = "h2r"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        output = determine_output_path(args.input, args.output)
        if args.intro:
            greenscreen_video = os.path.join(
                ASSETS, "humhaiRahicomingin-18mar25-working.m4v"
            )
            final_clip, fps = gs.overlay_greenscreen(
                args.input, greenscreen_video, "bottom", start_time=args.start_time
            )
            gs.write_clip(final_clip, output, fps)

        elif args.subscribe_voice:
            greenscreen_video = os.path.join(
                ASSETS, "subscribe-consider-subscribing-working.mp4"
            )
            final_clip, fps = gs.overlay_greenscreen(
                args.input, greenscreen_video, "bottom", start_time=args.start_time
            )
            gs.write_clip(final_clip, output, fps)

        elif args.subscribe:
            greenscreen_video = os.path.join(ASSETS, "subscribe-working.mp4")
            final_clip, fps = gs.overlay_greenscreen(
                args.input, greenscreen_video, "bottom", start_time=args.start_time
            )
            gs.write_clip(final_clip, output, fps)

        elif args.consider:
            audio = os.path.join(ASSETS, "consider-subscribing.mp3")
            final_clip = snd.add_audio_to_video(args.input, audio, args.start_time)
            snd.write_clip(final_clip, output)

        elif args.apna_desh:
            audio = os.path.join(ASSETS, "apnadesh-apnapradesh.mp3")
            final_clip = snd.add_audio_to_video(args.input, audio, args.start_time)
            snd.write_clip(final_clip, output)

        elif args.like:
            audio = os.path.join(ASSETS, "like-comment.mp3")
            final_clip = snd.add_audio_to_video(args.input, audio, args.start_time)
            snd.write_clip(final_clip, output)

        elif args.watching:
            audio = os.path.join(ASSETS, "youarewatchingHHR.mp3")
            final_clip = snd.add_audio_to_video(args.input, audio, args.start_time)
            snd.write_clip(final_clip, output)

        elif args.part_of_series:
            audio = os.path.join(ASSETS, "partofseries.mp3")
            final_clip = snd.add_audio_to_video(args.input, audio, args.start_time)
            snd.write_clip(final_clip, output)

        elif args.stay_tuned:
            audio = os.path.join(ASSETS, "StayTunedForMoreUpdates.mp3")
            final_clip = snd.add_audio_to_video(args.input, audio, args.start_time)
            snd.write_clip(final_clip, output)

        else:
            self.parser.print_help()

    def hello(self, args):
        # this routine will be called when "vidtoolz "h2r is called."
        print("Hello! This is an example ``vidtoolz`` plugin.")


h2r_plugin = ViztoolzPlugin()
