
import { useParams } from 'react-router-dom'
import { Card } from 'antd'

import { TestQuestion } from '../components/TestQuestion'
import { Header } from '../components/Header'


export default function Question() {
    const { token } = useParams()
    return (
        <div>
            <Header token={token} />
            <Card
                title='回答结果'
            >
                <TestQuestion token={token} />
            </Card>
        </div>
    )
}
