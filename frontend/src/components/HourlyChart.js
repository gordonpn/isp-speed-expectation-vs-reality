import React from "react";
import Chart from "react-apexcharts";
import Axios from "axios";

class HourlyChart extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            options: {
                xaxis: {
                    categories: [],
                    labels: {
                        show: false
                    }
                },
                title: {
                    text: 'Hourly Graph',
                    align: 'center'
                },
                subtitle: {
                    text: 'Average internet speed throughout a day.',
                    align: 'center'
                },
                stroke: {
                    curve: 'smooth',
                    width: 3
                },
                markers: {
                    size: 0
                }
            },
            series: [
                {
                    name: "Speed (MB/s)",
                    data: []
                }
            ]
        };
    }

    componentDidMount() {
        this.loadData();
    }

    async loadData() {
        await Axios.get('/api/hourly')
            .then(result => {
                let xaxis = [];
                let yaxis = [];
                result.data.forEach(item => {
                    xaxis.push(item[0]);
                    yaxis.push(item[1])
                });
                this.setState({
                    options: {
                        xaxis: {
                            categories: xaxis
                        }
                    },
                    series: [
                        {
                            data: yaxis
                        }
                    ]
                })
            })
    }

    render() {
        return (
            <div>
                <Chart
                    options={this.state.options}
                    series={this.state.series}
                    type="line"
                />
            </div>
        );
    }
}

export default HourlyChart;