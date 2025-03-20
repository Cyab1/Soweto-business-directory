import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getBusiness, getReviews } from '../services/api';
import ReviewForm from '../components/ReviewForm';

const BusinessDetails = () => {
    const { id } = useParams();
    const [business, setBusiness] = useState(null);
    const [reviews, setReviews] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            const businessData = await getBusiness(id);
            const reviewsData = await getReviews(id);
            setBusiness(businessData);
            setReviews(reviewsData);
        };
        fetchData();
    }, [id]);

    if (!business) return <div>Loading...</div>;

    return (
        <div className="container mt-5">
            <h1>{business.name}</h1>
            <p>{business.address}</p>
            <p>{business.contact_info}</p>
            <h2>Reviews</h2>
            {reviews.map((review) => (
                <div key={review.id} className="mb-3">
                    <p>{review.comment}</p>
                    <p>Rating: {review.rating}</p>
                </div>
            ))}
            <ReviewForm businessId={id} />
        </div>
    );
};

export default BusinessDetails;