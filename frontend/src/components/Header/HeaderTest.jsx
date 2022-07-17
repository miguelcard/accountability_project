import React from 'react'
import * as ReactBootStrap from 'react-bootstrap'
import '../../assets/styles/components/Header/Header.css'

function HeaderTest() {
    return (
      <div>
        <ReactBootStrap.Navbar collapseOnSelect expand="md" variant="dark" className='all-content'>
          <ReactBootStrap.Navbar.Brand href="/" className='logo'><h1>SupptMe</h1></ReactBootStrap.Navbar.Brand>
          <ReactBootStrap.Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <ReactBootStrap.Navbar.Collapse id="responsive-navbar-nav">
            <ReactBootStrap.Nav className="mr-auto">
            </ReactBootStrap.Nav>
            <ReactBootStrap.Nav>
              <ReactBootStrap.Nav.Link href="#deets" className="section-btn-items" id='home'>Home</ReactBootStrap.Nav.Link>
              <ReactBootStrap.Nav.Link href="#deets" className="section-btn-items" id='accountability'>Accountability</ReactBootStrap.Nav.Link>
              <ReactBootStrap.Nav.Link href="#deets" className="section-btn-items" id='about'>About</ReactBootStrap.Nav.Link>
              <ReactBootStrap.Nav.Link href="/login" className="section-btn-items" id='login'>Login</ReactBootStrap.Nav.Link>
            </ReactBootStrap.Nav>
          </ReactBootStrap.Navbar.Collapse>
        </ReactBootStrap.Navbar>
      </div>
    );
}

export default HeaderTest
