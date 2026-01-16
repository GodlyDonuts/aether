import { LineChart, Line, ResponsiveContainer } from 'recharts';

export const Sparkline = ({ data, color = "#10b981" }: { data: any[], color?: string }) => {
    return (
        <div className="h-[40px] w-[80px]">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                    <Line
                        type="monotone"
                        dataKey="value"
                        stroke={color}
                        strokeWidth={2}
                        dot={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};
