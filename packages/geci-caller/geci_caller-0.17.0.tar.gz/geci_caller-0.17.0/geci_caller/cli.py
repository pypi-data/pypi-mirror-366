from geci_caller.call_api import construct_entrypoint_url
import geci_caller as gc
import json
import pandas as pd
import requests
import typer
import io

cli = typer.Typer()


@cli.command()
def plot_cumulative_series_cpue_by_flight(
    input_path: str = typer.Option(help="Path of input data"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    url = construct_entrypoint_url(
        "eradication_progress",
        10000,
        "/plot_cumulative_series_cpue_by_flight",
        input_path=input_path,
        output_path=output_path,
    )
    response = requests.get(url)
    print(response.status_code)


@cli.command()
def plot_comparative_catch_curves(
    socorro_path: str = typer.Option(help="Path of Socorro data"),
    guadalupe_path: str = typer.Option(help="Path of Guadalupe data"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    url = construct_entrypoint_url(
        "eradication_progress",
        10000,
        "/plot_comparative_catch_curves",
        socorro_path=socorro_path,
        guadalupe_path=guadalupe_path,
        output_path=output_path,
    )
    response = requests.get(url)
    print(response.status_code)


@cli.command()
def write_bootstrap_progress_intervals(
    input_path: str = typer.Option(help="Path of input data"),
    bootstrapping_number: int = typer.Option(help="Number of bootstraps"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    entrypoint_name = "/write_bootstrap_progress_intervals_json"
    get_eradication_progress(
        entrypoint_name,
        input_path=input_path,
        bootstrapping_number=bootstrapping_number,
        output_path=output_path,
    )


@cli.command()
def filter_by_method(
    input_path: str = typer.Option(help="Path of input data"),
    method: str = typer.Option(help="Extraction method"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    entrypoint_name = "/filter_by_method"
    get_eradication_progress(
        entrypoint_name,
        input_path=input_path,
        method=method,
        output_path=output_path,
    )


@cli.command()
def write_aerial_monitoring(
    input_path: str = typer.Option(help="Path of input data"),
    bootstrapping_number: int = typer.Option(help="Number of bootstraps"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    get_eradication_progress_write_aerial_monitoring(
        input_path=input_path,
        bootstrapping_number=bootstrapping_number,
        output_path=output_path,
    )


@cli.command()
def write_population_status_from_mixed_methods(
    first_method_status: str = typer.Option(),
    second_method_status: str = typer.Option(),
    output_path: str = typer.Option(),
):
    entrypoint_name = "/write_population_status_from_mixed_methods"
    get_eradication_progress(
        entrypoint_name,
        first_method_status=first_method_status,
        second_method_status=second_method_status,
        output_path=output_path,
    )


@cli.command()
def write_population_status(
    input_path: str = typer.Option(help="Path of input data"),
    bootstrapping_number: int = typer.Option(help="Number of bootstraps"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    entrypoint_name = "/write_population_status"
    url = f"http://islasgeci.org:100{entrypoint_name}"
    with open(input_path, "rb") as f:
        response = requests.post(
            url,
            files={"file": f},
            data={"bootstrapping_number": bootstrapping_number},
        )
    response.raise_for_status()
    with open(output_path, "w") as out_file:
        json.dump(response.json(), out_file, indent=2)


@cli.command()
def write_csv_probability(
    input_path: str = typer.Option(help="Path of input data"),
    bootstrapping_number: int = typer.Option(help="Number of bootstrap by window"),
    output_path: str = typer.Option(help="Path of csv file to write"),
    window_length: int = typer.Option(help="Number of months by window"),
):
    entrypoint_name = "/write_effort_and_captures_with_probability"
    url = f"http://islasgeci.org:100{entrypoint_name}"
    with open(input_path, "rb") as f:
        response = requests.post(
            url,
            files={"file": f},
            data={
                "bootstrapping_number": bootstrapping_number,
                "window_length": window_length,
            },
        )
    response.raise_for_status()
    json_data = response.json()
    df = pd.DataFrame(json_data)
    df.to_csv(output_path, index=False)


@cli.command()
def write_probability_progress_figure(
    input_path: str = typer.Option(help="Path of input data"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    url = "http://islasgeci.org:100/write_probability_figure"
    file_like = read_file_as_buffer(input_path)
    files = {"file": (input_path, file_like, "text/csv")}
    response = requests.post(url, files=files)
    write_response_content(output_path, response)
    print(response.status_code)
    return response


@cli.command()
def plot_custom_cpue_vs_cum_captures(
    input_path: str = typer.Option(help="Path of input data"),
    config_path: str = typer.Option(help="Path of config file"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    url = "http://islasgeci.org:100/plot_custom_cpue_vs_cum_captures"
    file_like = read_file_as_buffer(input_path)
    config_like = read_file_as_buffer(config_path)
    files = {
        "file": (input_path, file_like, "text/csv"),
        "config": (config_path, config_like, "application/json"),
    }
    extension = output_path.split(".")[-1]
    response = requests.post(url, files=files, data={"format": extension})
    write_response_content(output_path, response)
    print(response.status_code)
    return response


@cli.command()
def plot_cpue_vs_cum_captures(
    input_path: str = typer.Option(help="Path of input data"),
    output_path: str = typer.Option(help="Path of figure to write"),
):
    extension = output_path.split(".")[-1]
    url = "http://islasgeci.org:100/plot_cpue_vs_cum_captures"
    file_like = read_file_as_buffer(input_path)
    files = {"file": (input_path, file_like, "text/csv")}
    response = requests.post(url, files=files, data={"format": extension})
    write_response_content(output_path, response)
    print(response.status_code)
    return response


@cli.command()
def version():
    version = gc.__version__
    print(version)


def read_file_as_buffer(file_path):
    with open(file_path, "rb") as file:
        buffer_file = io.BytesIO(file.read())
    return buffer_file


def get_eradication_progress(entrypoint_name, **kwargs):
    url = construct_entrypoint_url("eradication_progress", 10000, entrypoint_name, **kwargs)
    response = requests.get(url)
    print(response.status_code)


def write_response_content(output_path, response):
    with open(output_path, "wb") as out_file:
        out_file.write(response.content)


def get_eradication_progress_write_aerial_monitoring(**kwargs):
    url = construct_entrypoint_url_write_aerial_monitoring(**kwargs)
    response = requests.get(url)
    print(response.status_code)


def construct_entrypoint_url_write_aerial_monitoring(input_path, bootstrapping_number, output_path):
    return construct_entrypoint_url(
        "eradication_progress",
        10000,
        "/write_aerial_monitoring",
        input_path=input_path,
        bootstrapping_number=bootstrapping_number,
        output_path=output_path,
    )
