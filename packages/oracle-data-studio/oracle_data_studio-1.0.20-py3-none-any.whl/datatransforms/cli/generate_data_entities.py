'''
Licensed under the Universal Permissive License v 1.0 as shown at 
https://oss.oracle.com/licenses/upl/.

 Copyright (c) 2023, 2025, Oracle and/or its affiliates.

Utility script that generates data entities for given connection and schema
'''
from datatransforms.cli import cli_common
from datatransforms.generators.metadata_code_generator import DataEntityCodeGenerator

parser = cli_common.parser

parser.add_argument(
    "--connection",
    help="valid connection name available in the datatransforms deployment",
    required=True)
parser.add_argument("--schema", help="valid schema name available in the connection",required=True)
parser.add_argument("--live", type=cli_common.arg_to_bool, \
                    help="True- to generate data entities from connection directly, \
                        False - to generate from already discovered entities ONLY. \
                            Default is True")
parser.add_argument("--matching",
                    help="Generates only matching data entities, Ex ABC*|FGH* - only entities \
                    starts with ABC or FGH")

args = cli_common.process_args(parser)
print ("Generating data entities using options ...\n" + str(args) + "\n\n")

generator=DataEntityCodeGenerator()
generator.generate_data_entities_script(
    connection_name=args.connection,
    schema_name=args.schema,
    live=args.live,
    matching=args.matching)

print("DataEntity Generation Complete")
