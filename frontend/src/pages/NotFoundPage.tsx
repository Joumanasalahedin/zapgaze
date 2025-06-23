import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
    return (
        <div>
            <div>
                <div>
                    <h1>404</h1>
                    <h2>Page Not Found</h2>
                    <p>
                        The page you're looking for doesn't exist.
                    </p>
                    <Link
                        to="/"
                    >
                        Go Home
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default NotFoundPage;

// TODO: Beautify 404 page