def define_generate_parser(subparsers) -> str:
    """
    Defines the parser for the 'generate' command in the CLI.

    :param subparsers: The subparsers object to add the 'generate' command parser to.
    :return: The name of the subcommand.
    """

    # Subcommand: generate
    generate_parser = subparsers.add_parser(
        "generate", help="Generate a deck from an input file."
    )
    generate_parser.add_argument(
        "--input-file",
        "-i",
        required=True,
        help="Path to the input file (e.g., .txt, .md). Defaults to input.txt",
    )
    generate_parser.add_argument(
        "--output",
        "-o",
        required=False,
        default="output.apkg",
        help='Directory to save the generated deck, by default "output.apkg"',
    )
    generate_parser.add_argument("--name", "-n", required=True, help="Name of the deck")

    subcommand = "generate"
    return subcommand


def define_env_parser(subparsers) -> str:
    """
    Defines the parser for the 'env' command in the CLI.

    :param subparsers: The subparsers object to add the 'env' command parser to.
    :return: The name of the subcommand.
    """
    # subcommand set-env: used to set OpenAI API key
    env_parser = subparsers.add_parser(
        "env",
        help="Set OpenAI API, organization, and project ID environment variables.",
    )

    env_parser.add_argument(
        "--openai-api-key",
        "-k",
        required=True,
        help="OpenAI API key to use for requests.",
    )

    env_parser.add_argument(
        "--openai-organization-id",
        "-o",
        required=False,
        help="OpenAI organization ID to use for requests.",
    )
    env_parser.add_argument(
        "--openai-project-id",
        "-p",
        required=False,
        help="OpenAI project ID to use for requests.",
    )

    command = "env"
    return command
