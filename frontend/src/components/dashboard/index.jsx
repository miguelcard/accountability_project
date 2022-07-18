import React from 'react'
import { Jumbotron, Button, Container } from 'reactstrap';
import '../../assets/styles/components/dashboard/index.css'
import CarouselDashboard from './carousel';

const Dashboard = (props) => {
    return (
        <>
            <Jumbotron fluid id="content-dashboard">
                <Container fluid="xl" className="dashboard-col-1">
                    <h1 className="display-5">Here’s How You’re Doing So Far...</h1>
                </Container>
                <Container fluid className="dashboard-col-2">
                    <Container fluid className="sub-dashboard-col-1">
                        <h1 className="display-5">Great, you’ve logged habits on the past 4 days!</h1>
                    </Container>
                </Container>
                <Container fluid className="dashboard-col-3">
                    <Container fluid className="sub-dashboard-3-col-1">
                        <h1 className="display-3">Upcoming Goals:</h1>
                        <p className="lead">Learn a new language (watch 100 modules)</p>
                        <p className="lead">Wake up at 4:30am (20 times this month)</p>
                    </Container>
                </Container>
                <Container fluid className="dashboard-col-4">
                    <Container fluid className="sub-dashboard-4-col-1">
                        <h1 className="display-3">Upcoming Goals:</h1>
                    </Container>
                    <CarouselDashboard/>
                </Container>
                <Container fluid="xl" className="dashboard-col-5">
                    <h1 className="display-3">Hello, world!</h1>
                    <p className="lead">This is a simple hero unit, a simple Jumbotron-style component for calling extra attention to featured content or information.</p>
                    <hr className="my-2" />
                    <p>It uses utility classes for typography and spacing to space content out within the larger container.</p>
                    <p className="lead">
                        <Button color="primary">Learn More</Button>
                    </p>
                </Container>
            </Jumbotron>
        </>
    )
}

export default Dashboard
